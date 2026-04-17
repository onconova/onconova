from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, TypeVar, get_origin

import pghistory
from django.db import transaction
from django.db.models import Model as DjangoModel
from ninja import Schema

from onconova.core.auth.models import User
from onconova.core.auth.schemas import UserExport
from onconova.interoperability.schemas import PatientCaseBundle
from onconova.oncology import models, schemas

T = TypeVar("T", bound=DjangoModel)


@dataclass
class NestedResourceDetails:
    orm_related_name: str
    schema_related_name: str
    instance_init: Callable


class BundleParser:

    def __init__(self, bundle: PatientCaseBundle):
        self.bundle = bundle
        self.key_map = defaultdict(dict)
        self.users_map = {}
        # Import all other resources
        self.list_fields = [
            field_name
            for field_name, field_info in self.bundle.__class__.model_fields.items()
            if get_origin(field_info.annotation) is list
            and field_name not in ["history", "contributorsDetails"]
        ]
        self.users_map = {user.username: user for user in bundle.contributorsDetails}
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
    def get_or_create_user(user: UserExport) -> User:
        """
        Retrieves an existing User object by username or creates a new one if it does not exist.

        Args:
            user (User | str): A User instance containing user details, or a string representing the username.

        Returns:
            User: The retrieved or newly created User object, or None if the input is invalid.

        Notes:
            - If a string is provided, a new user is created with default inactive and external access level.
            - If a User is provided, user details are imported and the user is created as inactive and external.
        """
        # CHeck if internal user exist
        if internal_user := User.objects.filter(
            username=user.username, email=user.email
        ).first():
            return internal_user
        organization_initials = "".join([word[0].lower() for word in (user.organization).split(" ")]) if user.organization else "ext"  # type: ignore
        username = f"{user.username}-{organization_initials}"
        return User.objects.get_or_create(
            username=username,
            defaults=dict(
                # Import details of the external user
                first_name=user.firstName,
                last_name=user.lastName,
                email=user.email,
                organization=user.organization,
                external_source=user.externalSource or user.organization,
                external_source_id=user.externalSourceId or user.id,
                # Assign new user as inactive & external (access level zero)
                access_level=0,
                is_active=False,
            ),
        )[0]

    def _update_key_map(
        self, orm_instance: DjangoModel, schema_instance: Schema
    ) -> None:
        """
        Updates the key_map dictionary by mapping the schema_instance's ID to the orm_instance's ID.

        Args:
            orm_instance (DjangoModel): The ORM model instance whose ID will be mapped.
            schema_instance (Schema): The schema instance whose ID will be used as the key.

        Returns:
            None
        """
        self.key_map[getattr(schema_instance, "id", "")] = getattr(
            orm_instance,
            "id",
        )

    def _get_internal_key(self, external_key: str) -> dict:
        """
        Retrieves the internal key mapping for a given external key.

        Args:
            external_key (str): The external key to look up.

        Returns:
            dict: The corresponding internal key mapping.

        Raises:
            KeyError: If the external_key is not found in key_map.
        """
        return self.key_map[external_key]

    def _get_unresolvable_keys(self, schema_instance: Schema) -> list[str]:
        """
        Returns a list of external key IDs referenced by the schema instance
        that are not yet present in the key_map.

        Args:
            schema_instance (Schema): The schema instance to inspect.

        Returns:
            list[str]: External key values that cannot currently be resolved.
        """
        unresolvable = []
        for field_name in [
            field
            for field in schema_instance.__class__.model_fields
            if field not in ["externalSourceId"]
        ]:
            if field_name.endswith("Id"):
                external_key = getattr(schema_instance, field_name)
                if external_key and external_key not in self.key_map:
                    unresolvable.append(external_key)
            elif field_name.endswith("Ids"):
                for key in getattr(schema_instance, field_name) or []:
                    if key not in self.key_map:
                        unresolvable.append(key)
        return unresolvable

    def resolve_foreign_keys(self, schema_instance: Schema) -> Schema:
        """
        Resolves foreign key fields in a schema instance by converting external keys to internal keys.

        Iterates over the fields of the provided schema instance, excluding 'externalSourceId'.
        For fields ending with 'Id', replaces the external key value with its corresponding internal key.
        For fields ending with 'Ids', replaces the list of external key values with a list of corresponding internal keys.

        Args:
            schema_instance (Schema): The schema instance containing foreign key fields to resolve.

        Returns:
            Schema: The schema instance with foreign key fields resolved to internal keys.
        """
        for field_name in [
            field
            for field in schema_instance.__class__.model_fields
            if field not in ["externalSourceId"]
        ]:
            if field_name.endswith("Id"):
                external_key = getattr(schema_instance, field_name)
                if external_key:
                    setattr(
                        schema_instance,
                        field_name,
                        self._get_internal_key(external_key),
                    )
            elif field_name.endswith("Ids"):
                external_keys = getattr(schema_instance, field_name)
                if external_keys:
                    setattr(
                        schema_instance,
                        field_name,
                        [
                            self._get_internal_key(external_key)
                            for external_key in external_keys
                        ],
                    )
        return schema_instance

    def import_history_events(self, orm_instance: DjangoModel, resourceId: str) -> None:
        """
        Imports history events associated with a specific resource into the ORM instance.

        This method filters events from the bundle's history that match the given resourceId,
        imports the user (actor) for each event if present, creates event records in the ORM,
        manually sets the event timestamp, and finally adds a manual event indicating the import.

        Args:
            orm_instance (DjangoModel): The ORM instance to which events will be imported.
            resourceId (str): The identifier of the resource whose events are to be imported.
        """
        events = [
            event
            for event in self.bundle.history
            if str(event.resourceId) == str(resourceId)
        ]
        for event in events:
            if event.user:
                user = self.users_map.get(event.user)
                if not user:
                    raise ValueError(f"Unknown user in bundle definition: {event.user}")
                # Import the actor of the event
                user = self.get_or_create_user(user)
            # Manually import the event metadata
            event_instance = orm_instance.events.create(  # type: ignore
                pgh_obj=orm_instance,
                pgh_label=event.category,
                pgh_context=dict(username=user.username if event.user else None),
            )
            # Override the automated timestamp on the event
            orm_instance.events.filter(pk=event_instance.pk).update(  # type: ignore
                pgh_created_at=event.timestamp
            )
        # Add a manual event for the importing of the data
        pghistory.create_event(orm_instance, label="import")

    def import_resource(
        self, resource: Schema, instance: T | None = None, **fields
    ) -> T:
        """
        Imports a resource into the database, resolving foreign keys and associating related events.

        Args:
            resource (Schema): The resource object to import, which must have an 'id' attribute.
            instance (T | None, optional): An existing ORM instance to update, or None to create a new one.
            fields (dict): Additional fields to pass to the model's dump method.

        Raises:
            ValueError: If the resource does not have an 'id'.

        Returns:
            The ORM instance created or updated from the resource.

        Side Effects:
            - Resolves foreign keys in the resource.
            - Creates or updates the database entry for the resource.
            - Deletes the latest creation event for the ORM instance.
            - Updates the external-to-internal foreign key mapping.
            - Imports related history events for the resource.
        """
        if not getattr(resource, "id", None):
            raise ValueError("Resource must have an ID to be imported.")
        # Get the model-create schema for the resource
        CreateSchema = getattr(
            schemas, f"{resource.__class__.__name__}CreateSchema", None
        ) or getattr(schemas, f"{resource.__class__.__name__}Create")
        # Resolve any foreign keys in the resource
        resource = self.resolve_foreign_keys(resource)
        resourceId = resource.id  # type: ignore
        # Create the database entry for the resource
        orm_instance = CreateSchema.model_validate(resource).model_dump_django(
            instance=instance,
            **fields,
            external_source=resource.externalSource or "Onconova",  # type: ignore
            external_source_id=resource.externalSourceId or resourceId,  # type: ignore
        )
        # Delete the create event that just happened
        orm_instance.events.latest("pgh_created_at").delete()
        # Update the external-to-internal foreign key map
        self._update_key_map(orm_instance, resource)
        self.import_history_events(orm_instance, resourceId)
        return orm_instance

    def import_bundle(self, case=None) -> models.PatientCase:
        """
        Imports a patient case bundle into the database, including all related resources and data completion statuses.

        This method performs the import within a database transaction to ensure atomicity and prevent partial imports in case of errors.
        It validates and imports the main patient case, then iterates through all related resource lists, importing each resource and its nested subresources.
        Finally, it records the completion status for each data category associated with the case.

        Args:
            case (models.PatientCase, optional): An existing PatientCase instance to update. If None, a new instance is created.

        Returns:
            models.PatientCase: The imported or updated PatientCase instance.
        """
        # Conduct the import within a transaction to avoid partial imports in case of an error
        with transaction.atomic():
            # Import the patient case
            case_schema = schemas.PatientCase.model_validate(self.bundle)
            imported_case = self.import_resource(
                case_schema,
                instance=case,
                pseudoidentifier=self.bundle.pseudoidentifier,  # type: ignore
            )
            # Collect all top-level resources to import
            pending = [
                (list_field, resource)
                for list_field in self.list_fields
                for resource in getattr(self.bundle, list_field)
            ]
            # Multi-pass import so that forward references are resolved once the
            # referenced resource has been imported in a previous iteration.
            while pending:
                previously_pending_count = len(pending)
                deferred = []
                for list_field, resource in pending:
                    # Collect unresolvable keys for the resource AND all its nested subresources
                    # so that a parent is not imported before its children's FK targets exist.
                    all_unresolvable = self._get_unresolvable_keys(resource)
                    for nested_resource_details in self.nested_resources.get(
                        list_field, []
                    ):
                        for nested_resource in getattr(
                            resource, nested_resource_details.schema_related_name, []
                        ):
                            all_unresolvable.extend(
                                self._get_unresolvable_keys(nested_resource)
                            )
                    if all_unresolvable:
                        deferred.append((list_field, resource))
                        continue
                    orm_resource = self.import_resource(resource)
                    # Import any nested subresources immediately after their parent
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
                if len(deferred) == previously_pending_count:
                    # No progress was made — references are either missing or circular
                    def _all_unresolvable(list_field, r):
                        keys = self._get_unresolvable_keys(r)
                        for nrd in self.nested_resources.get(list_field, []):
                            for nr in getattr(r, nrd.schema_related_name, []):
                                keys.extend(self._get_unresolvable_keys(nr))
                        return keys

                    unresolved_details = [
                        f"{r.__class__.__name__} (id={getattr(r, 'id', 'unknown')}, "
                        f"unresolved references: {_all_unresolvable(lf, r)})"
                        for lf, r in deferred
                    ]
                    raise ValueError(
                        f"Cannot resolve external ID references for the following resources: "
                        f"{'; '.join(unresolved_details)}. "
                        f"Ensure all referenced resources are included in the bundle."
                    )
                pending = deferred
            # Import data completion status
            for category, completion in self.bundle.completedDataCategories.items():
                if completion.status:
                    with pghistory.context(username=completion.username):
                        models.PatientCaseDataCompletion.objects.create(
                            case=imported_case, category=category
                        )
            # Re-assign therapy lines
            models.TherapyLine.assign_therapy_lines(imported_case)
        return imported_case
