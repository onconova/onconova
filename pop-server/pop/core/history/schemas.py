from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from ninja import Schema
from pydantic import Field, AliasChoices


class HistoryEventCategory(str, Enum):
    """
    Enumeration of possible history event categories.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    DOWNLOAD = "download"


class HistoryEvent(Schema):
    """
    Represents an audit/history event capturing changes in the system.
    """

    id: Any = Field(
        title="Event ID",
        description="The unique identifier of the history event",
        alias="pgh_id",
        validation_alias=AliasChoices("id", "pgh_id"),
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
    user: Optional[str] = Field(
        default=None,
        title="User",
        description="Username of the user that triggered the event, if applicable",
    )
    url: Optional[str] = Field(
        default=None,
        title="Endpoint",
        description="Endpoint URL through which the event was triggered, if applicable",
    )
    snapshot: Dict = Field(
        title="Data snapshopt",
        description="Data snapshopt at the time of the event",
    )
    differential: Optional[Dict] = Field(
        title="Data differential",
        description="Data changes introduced by the event, if applicable",
    )
    context: Optional[Dict] = Field(
        title="Context",
        description="Context sorrounding the event",
        alias="pgh_context",
        validation_alias=AliasChoices("context", "pgh_context"),
    )

    @staticmethod
    def resolve_user(obj):
        """
        Extract the username from the event's context.

        Args:
            obj (Any): The history event object.

        Returns:
            Optional[str]: The username if present.
        """
        return obj.pgh_context["username"]

    @staticmethod
    def resolve_category(obj):
        """
        Resolve the event category from its label.

        Args:
            obj (Any): The history event object.

        Returns:
            Optional[HistoryEventCategory]: The corresponding event category.
        """
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
            Dict[str, Any]: The data snapshot.
        """
        return obj.pgh_data

    @staticmethod
    def resolve_differential(obj):
        """
        Retrieve the data differential from the event.

        Args:
            obj (Any): The history event object.

        Returns:
            Optional[Dict[str, Any]]: The data changes if present.
        """
        return obj.pgh_diff

    @classmethod
    def bind_schema(cls, schema: Schema):
        """
        Dynamically bind a specific Pydantic schema to the history event.

        This allows resolving snapshot and differential data using the target schema
        for automatic foreign key resolution and data validation.

        Args:
            schema (Type[Schema]): The target Pydantic schema.

        Returns:
            Type[HistoryEvent]: A new HistoryEvent schema subclass with schema-bound resolvers.
        """

        class HistoryEventWithSchema(cls):
            @staticmethod
            def resolve_snapshot(obj):
                # Create a new instance of the model based on snapshot data to automatically resolve foreign keys
                try:
                    instance = schema.get_orm_model()(
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
                if obj.pgh_diff:
                    return schema.model_construct(**obj.pgh_diff).model_dump(
                        exclude_defaults=True
                    )

        return HistoryEventWithSchema
