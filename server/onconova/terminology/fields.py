from typing import Literal, TypeVar, overload

from django.core.exceptions import FieldError
from django.db import models

from onconova.terminology.models import CodedConcept

CodedConceptModel = TypeVar("CodedConceptModel", bound=CodedConcept)


@overload
def CodedConceptField(
    terminology: type[CodedConceptModel],
    *,
    multiple: Literal[False] = False,
    null: Literal[False] = False,
    blank=False,
    _to: type[CodedConceptModel] | None = None,
    on_delete=models.PROTECT,
    **kwargs,
) -> models.ForeignKey[CodedConceptModel]: ...


@overload
def CodedConceptField(
    terminology: type[CodedConceptModel],
    *,
    multiple: Literal[False] = False,
    null: Literal[True],
    blank=False,
    _to: type[CodedConceptModel] | None = None,
    on_delete=models.PROTECT,
    **kwargs,
) -> models.ForeignKey[CodedConceptModel | None]: ...


@overload
def CodedConceptField(
    terminology: type[CodedConceptModel],
    *,
    multiple: Literal[True],
    null: Literal[False] = False,
    blank=False,
    _to: type[CodedConceptModel] | None = None,
    on_delete=models.PROTECT,
    **kwargs,
) -> models.ManyToManyField: ...


def CodedConceptField(
    terminology: type[CodedConceptModel],
    multiple=False,
    null=False,
    blank=False,
    _to: type[CodedConceptModel] | None = None,
    on_delete=models.PROTECT,
    **kwargs,
) -> (
    models.ForeignKey[CodedConceptModel]
    | models.ForeignKey[CodedConceptModel | None]
    | models.ManyToManyField
):
    """
    Factory function for creating a Django relation field (ForeignKey or ManyToManyField) to a terminology model.

    Args:
        terminology (type[CodedConceptModel]): The target model class for the relationship.
        multiple (bool, optional): If True, returns a ManyToManyField; if False, returns a ForeignKey. Defaults to False.
        null (bool, optional): If True, allows null values. Used only for ManyToManyField. Defaults to False.
        blank (bool, optional): If True, allows blank values. Defaults to False.
        _to (type[CodedConceptModel] | None, optional): Alternate target model for the relationship. If provided, overrides terminology. Defaults to None.
        on_delete (Any, optional): Deletion behavior for ForeignKey. Defaults to models.PROTECT.
        kwargs (dict): Additional keyword arguments passed to the underlying field.

    Returns:
        (models.ForeignKey[CodedConceptModel] | models.ForeignKey[CodedConceptModel | None] | models.ManyToManyField):
            A Django ForeignKey field (if multiple=False) or ManyToManyField (if multiple=True) configured to point to the terminology model.

    Raises:
        AssertionError: If neither terminology nor _to is specified.
    """
    multiple = multiple
    terminology = _to or terminology
    assert (
        terminology is not None
    ), "Either terminology or _to arguments must be specified"
    terminology = terminology
    _on_delete = on_delete
    _kwargs: dict = dict(blank=blank, **kwargs)

    if multiple:
        field = models.ManyToManyField(
            to=terminology,
            related_name="+",
            **_kwargs,
        )
    else:
        field = models.ForeignKey(
            to=terminology,
            on_delete=_on_delete,
            related_name="+",
            null=null,
            **_kwargs,
        )
    return field


class DescendsFrom(models.Lookup):
    lookup_name = "descendsfrom"

    def get_prep_lookup(self):
        """
        Prepares the right-hand side (rhs) of the lookup before executing a query.

        This method ensures that the lookup is only applied to fields of type
        CodedConceptField by checking the alias of the left-hand side (lhs). If the
        rhs is an instance of a Django model, it converts rhs to the primary key of
        that model. It then calls the parent class's get_prep_lookup method for any
        additional preparation.

        Raises:
            FieldError: If the lookup is not applied to a CodedConceptField field.
        """
        if not "terminology" in self.lhs.alias:
            raise FieldError(
                f"Lookup {self.lookup_name} is only supported for CodedConceptField fields."
            )
        if isinstance(self.rhs, models.Model):
            self.rhs = self.rhs.pk
        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        """
        Converts the lookup into SQL.

        This method is overridden from the Lookup class to create a recursive
        CTE query that traverses the parent-child relationships of the
        CodedConceptField.

        Args:
            compiler (Any): The SQLCompiler instance.
            connection (Any): The database connection.

        Returns:
            (tuple[str, list[int, str]]): A tuple of the SQL query and parameters.

        """
        # Get the left-hand and right-hand sides of the lookup
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # Construct the parameters
        params = lhs_params + rhs_params

        # Get the table name of the left-hand side
        table = lhs.split(".")[0].strip('"')

        # Construct the recursive CTE query
        recursive_cte = f"""
		WITH RECURSIVE descendants AS (
			SELECT id
			FROM {table}
			WHERE id = {rhs}
			UNION ALL
			SELECT t.id
			FROM {table} AS t
			INNER JOIN descendants AS d ON t.parent_id = d.id
		)
		SELECT id FROM descendants
		"""

        # Return the SQL query and parameters
        return "%s IN (%s)" % (lhs, recursive_cte), params


models.ForeignKey.register_lookup(DescendsFrom)
