from django.db import transaction
from django.db.models import Model as DjangoModel
from pop.oncology import schemas
from pop.core.auth.models import User
from collections import defaultdict
from pop.oncology import models
from ninja import Schema
import pghistory
from pop.core.auth.schemas import UserSchema
from pop.interoperability.schemas import PatientCaseBundle
from typing import get_origin, Optional
from dataclasses import dataclass


@dataclass
class NestedResourceDetails:
    orm_related_name: str
    schema_related_name: str
    instance_init: callable


class BundleParser:

    def __init__(self, bundle: PatientCaseBundle):
        self.bundle = bundle
        self.key_map = defaultdict(dict)
        # Import all other resources
        self.list_fields = [
            field_name
            for field_name, field_info in self.bundle.model_fields.items()
            if get_origin(field_info.annotation) is list
            and field_name not in ["updatedBy"]
        ]
        self.nested_resources = {
            "systemicTherapies": [
                NestedResourceDetails(
                    "medications",
                    "medications",
                    lambda resource: models.SystemicTherapyMedication(
                        systemic_therapy=resource
                    ),
                )
            ],
            "radiotherapies": [
                NestedResourceDetails(
                    "dosages",
                    "dosages",
                    lambda resource: models.RadiotherapyDosage(radiotherapy=resource),
                ),
                NestedResourceDetails(
                    "settings",
                    "settings",
                    lambda resource: models.RadiotherapySetting(radiotherapy=resource),
                ),
            ],
            "adverseEvents": [
                NestedResourceDetails(
                    "suspected_causes",
                    "suspectedCauses",
                    lambda resource: models.AdverseEventSuspectedCause(
                        adverse_event=resource
                    ),
                ),
                NestedResourceDetails(
                    "mitigations",
                    "mitigations",
                    lambda resource: models.AdverseEventMitigation(
                        adverse_event=resource
                    ),
                ),
            ],
            "tumorBoards": [
                NestedResourceDetails(
                    "therapeutic_recommendations",
                    "therapeuticRecommendations",
                    lambda resource: models.MolecularTherapeuticRecommendation(
                        molecular_tumor_board=resource
                    ),
                ),
            ],
        }

    @staticmethod
    def get_or_create_user(user: UserSchema | str) -> User:
        """Fetches or creates a user instance from the given schema."""
        if not user:
            return None
        if isinstance(user, str):
            return User.objects.get_or_create(
                username=user,
                defaults=dict(
                    # Assign new user as inactive & external (access level zero)
                    access_level=0,
                    is_active=False,
                ),
            )[0]
        else:
            return User.objects.get_or_create(
                username=user.username,
                defaults=dict(
                    # Import details of the external user
                    first_name=user.firstName,
                    last_name=user.lastName,
                    email=user.email,
                    title=user.title,
                    organization=user.organization,
                    department=user.department,
                    # Assign new user as inactive & external (access level zero)
                    access_level=0,
                    is_active=False,
                ),
            )[0]

    def update_key_map(
        self, orm_instance: DjangoModel, schema_instance: Schema
    ) -> None:
        self.key_map[schema_instance.id] = orm_instance.id

    def get_internal_key(self, external_key: str) -> str:
        return self.key_map[external_key]

    def resolve_foreign_keys(self, schema_instance: Schema) -> Schema:
        for field_name in schema_instance.model_fields:
            if field_name.endswith("Id"):
                external_key = getattr(schema_instance, field_name)
                if external_key:
                    setattr(
                        schema_instance, field_name, self.get_internal_key(external_key)
                    )
            elif field_name.endswith("Ids"):
                external_keys = getattr(schema_instance, field_name)
                if external_keys:
                    setattr(
                        schema_instance,
                        field_name,
                        [
                            self.get_internal_key(external_key)
                            for external_key in external_keys
                        ],
                    )
        return schema_instance

    def import_resource(
        self, schema_instance: Schema, instance: Optional[DjangoModel] = None
    ) -> DjangoModel:
        CreateSchema = getattr(
            schemas, f"{schema_instance.__class__.__name__}CreateSchema"
        )
        self.resolve_foreign_keys(schema_instance)
        orm_instance = CreateSchema.model_validate(schema_instance).model_dump_django(
            instance=instance
        )
        self.update_key_map(orm_instance, schema_instance)
        return orm_instance

    def import_bundle(self) -> models.PatientCase:
        # Conduct the import within a transaction to avoid partial imports in case of an error
        with transaction.atomic():
            # Import the core case datas
            case_schema = schemas.PatientCaseSchema.model_validate(self.bundle)
            imported_case = self.import_resource(case_schema)
            # Keep the imported pseudoidentifier
            imported_case.pseudoidentifier = self.bundle.pseudoidentifier
            imported_case.save()

            for list_field in self.list_fields:
                for resource in getattr(self.bundle, list_field):
                    orm_resource = self.import_resource(resource)
                    # Check if the resource has any nested subresources
                    for nested_resource_details in self.nested_resources.get(
                        list_field, []
                    ):
                        getattr(
                            orm_resource, nested_resource_details.orm_related_name
                        ).set(
                            [
                                self.import_resource(
                                    nested_resource,
                                    instance=nested_resource_details.instance_init(
                                        orm_resource
                                    ),
                                )
                                for nested_resource in getattr(
                                    resource,
                                    nested_resource_details.schema_related_name,
                                )
                            ]
                        )
            # Import data completion status
            for category, completion in self.bundle.completedDataCategories.items():
                if completion.status:
                    with pghistory.context(username=completion.username):
                        models.PatientCaseDataCompletion.objects.create(
                            case=imported_case, category=category
                        )
        return imported_case
