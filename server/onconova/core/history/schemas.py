from datetime import datetime
from enum import Enum
from typing import Any, Dict

from ninja import Schema
from pydantic import AliasChoices, Field

from onconova.core.models import BaseModel, UntrackedBaseModel
from onconova.core.serialization.base import BaseSchema
from onconova.core.types import Nullable


class HistoryEventCategory(str, Enum):
    """
    Enumeration of possible categories for history events.

    Attributes:
        CREATE: Represents the creation of an entity.
        UPDATE: Represents the update of an entity.
        DELETE: Represents the deletion of an entity.
        EXPORT: Represents the export of data.
        IMPORT: Represents the import of data.
        DOWNLOAD: Represents the download of data.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    DOWNLOAD = "download"


class HistoryEvent(Schema):
    """
    Schema representing a history event within the system.

    Attributes:
        id (Any): The unique identifier of the history event.
        resourceId (Any): The unique identifier of the tracked resource.
        category (HistoryEventCategory): The type of history event.
        timestamp (datetime): Timestamp of the history event.
        user (Nullable[str]): Username of the user that triggered the event, if applicable.
        url (Nullable[str]): Endpoint URL through which the event was triggered, if applicable.
        resource (Nullable[str]): Resource involved in the event, if applicable.
        snapshot (Dict): Data snapshot at the time of the event.
        differential (Nullable[Dict]): Data changes introduced by the event, if applicable.
        context (Nullable[Dict]): Context surrounding the event.
    """

    id: Any = Field(
        title="Event ID",
        description="The unique identifier of the history event",
        alias="pgh_id",
        validation_alias=AliasChoices("id", "pgh_id"),
    )
    resourceId: Any = Field(
        title="Resource ID",
        description="The unique identifier of the tracked resource",
        alias="pgh_obj_id",
        validation_alias=AliasChoices("resourceId", "pgh_obj_id"),
    )
    category: HistoryEventCategory = Field(
        title="Category",
        description="The type of history event",
        alias="pgh_label",
        validation_alias=AliasChoices("category", "pgh_label"),
    )
    timestamp: datetime = Field(
        title="Timestamp",
        description="Timestamp of the history event",
        alias="pgh_created_at",
        validation_alias=AliasChoices("timestamp", "pgh_created_at"),
    )
    user: Nullable[str] = Field(
        default=None,
        title="User",
        description="Username of the user that triggered the event, if applicable",
    )
    url: Nullable[str] = Field(
        default=None,
        title="Endpoint",
        description="Endpoint URL through which the event was triggered, if applicable",
    )
    resource: Nullable[str] = Field(
        default=None,
        title="Resource",
        description="Resource involved in the event, if applicable",
    )
    snapshot: Dict = Field(
        title="Data snapshopt",
        description="Data snapshopt at the time of the event",
    )
    differential: Nullable[Dict] = Field(
        title="Data differential",
        description="Data changes introduced by the event, if applicable",
    )
    context: Nullable[Dict] = Field(
        title="Context",
        description="Context sorrounding the event",
        alias="pgh_context",
        validation_alias=AliasChoices("context", "pgh_context"),
    )

    @staticmethod
    def resolve_resource(obj):
        """
        Extract the resource from the event's context.

        Args:
            obj (Any): The history event object.

        Returns:
            (str | None): The resource if present.
        """
        if isinstance(obj, dict):
            return obj.get("resource")
        return obj.pgh_obj_model.split(".")[-1]

    @staticmethod
    def resolve_url(obj):
        """
        Extract the url from the event's context.

        Args:
            obj (Any): The history event object.

        Returns:
            (str | None): The resource if present.
        """
        if isinstance(obj, dict):
            return obj.get("url")
        return obj.pgh_context.get("url")

    @staticmethod
    def resolve_user(obj):
        """
        Extract the username from the event's context.

        Args:
            obj (Any): The history event object.

        Returns:
            (str | None): The username if present.
        """
        if isinstance(obj, dict):
            return obj.get("user")
        return obj.pgh_context.get("username")

    @staticmethod
    def resolve_category(obj):
        """
        Resolve the event category from its label.

        Args:
            obj (Any): The history event object.

        Returns:
            (HistoryEventCategory | None): The corresponding event category.
        """
        if isinstance(obj, dict):
            return obj.get("category")
        return {
            "create": HistoryEventCategory.CREATE,
            "update": HistoryEventCategory.UPDATE,
            "delete": HistoryEventCategory.DELETE,
            "export": HistoryEventCategory.EXPORT,
            "import": HistoryEventCategory.IMPORT,
            "download": HistoryEventCategory.DOWNLOAD,
        }.get(obj.pgh_label)

    @staticmethod
    def resolve_snapshot(obj):
        """
        Retrieve the snapshot data from the event.

        Args:
            obj (Any): The history event object.

        Returns:
            (Dict[str, Any]): The data snapshot.
        """
        if isinstance(obj, dict):
            return obj.get("snapshot")
        return obj.pgh_data

    @staticmethod
    def resolve_differential(obj):
        """
        Retrieve the data differential from the event.

        Args:
            obj (Any): The history event object.

        Returns:
            (Dict[str, Any] | None): The data changes if present.
        """
        if isinstance(obj, dict):
            return obj.get("differential")
        return obj.pgh_diff

    @classmethod
    def bind_schema(cls, schema: type[BaseSchema]):
        """
        Dynamically bind a specific Pydantic schema to the history event.

        This allows resolving snapshot and differential data using the target schema
        for automatic foreign key resolution and data validation.

        Args:
            schema (Type[Schema]): The target Pydantic schema.

        Returns:
            (Type[HistoryEvent]): A new HistoryEvent schema subclass with schema-bound resolvers.
        """

        class HistoryEventWithSchema(cls):
            """
            HistoryEventWithSchema provides static methods to resolve snapshot and differential data from history event objects.
            """
            @staticmethod
            def resolve_snapshot(obj: Any) -> dict | None:
                """
                Resolves the snapshot data from the given object.

                If the object is a dictionary, returns the value associated with the "snapshot" key.
                If the object is not a dictionary, attempts to create a new instance of the ORM model using the object's `pgh_data`.
                Validates and serializes the model, merging its data with the instance's ID.
                If any exception occurs during model instantiation or validation, returns the raw `pgh_data`.

                Args:
                    obj (Any): The object containing snapshot or pgh_data information.

                Returns:
                   (dict | None): The resolved snapshot data as a dictionary, or None if not available.
                """
                if isinstance(obj, dict):
                    return obj.get("snapshot")
                # Create a new instance of the model based on snapshot data to automatically resolve foreign keys
                try:
                    instance: BaseModel | UntrackedBaseModel = schema.get_orm_model()(
                        **{key: val for key, val in obj.pgh_data.items()}
                    )
                    # Cast to model schema
                    return schema.model_validate(obj.pgh_data).model_dump(
                        exclude_unset=True
                    ) | {"id": instance.id}
                except:
                    return obj.pgh_data

            @staticmethod
            def resolve_differential(obj):
                """
                Resolves and returns the 'differential' data from the given object.

                If the input object is a dictionary, retrieves the value associated with the 'differential' key.
                If the input object has a 'pgh_diff' attribute, constructs a schema model from it and returns its dictionary representation,
                excluding default values.

                Args:
                    obj (dict | object): The object or dictionary containing differential data.

                Returns:
                    (dict | Any): The resolved differential data, or None if not found.
                """
                if isinstance(obj, dict):
                    return obj.get("differential")
                if obj.pgh_diff:
                    return schema.model_construct(**obj.pgh_diff).model_dump(
                        exclude_defaults=True
                    )

        return HistoryEventWithSchema
