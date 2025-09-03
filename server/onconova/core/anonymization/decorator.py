import inspect
from abc import ABC
from functools import wraps
from typing import Any, Callable, Iterable, Union, overload

from django.db.models import Model as DjangoModel
from django.db.models import QuerySet, Value
from django.http import HttpRequest
from ninja import Field, Query, Schema
from ninja.constants import NOT_SET
from ninja.errors import HttpError
from ninja.signature import is_async
from ninja_extra.controllers.route.context import RouteContext
from ninja_extra.shortcuts import add_ninja_contribute_args

from onconova.core.auth import permissions


class AnonymizationBase(ABC):
    """
    Base class for implementing anonymization logic in data access layers.

    Attributes:
        InputSource: Query parameter for input source (type: Query).
        Input (Schema): Nested schema class with an 'anonymized' boolean field to indicate whether data should be anonymized.

    Args:
        pass_parameter (str | None): Optional parameter to pass through the anonymization process.
        **kwargs (Any): Additional keyword arguments.

    Methods:
        anonymize_queryset(data, anonymized=True, **params):

                data (QuerySet | DjangoModel | Schema | Iterable[DjangoModel]): The data to be anonymized.
    """

    InputSource = Query(...)  # type: ignore

    class Input(Schema):
        anonymized: bool = Field(
            default=True,
            title="Anonymize",
            description="Whether to anonymize the data or not (requires elevated permissions)",
        )

    def __init__(self, *, pass_parameter: str | None = None, **kwargs: Any) -> None:
        self.pass_parameter = pass_parameter

    def anonymize_queryset(
        self,
        data: DjangoModel | Schema | Iterable[DjangoModel],
        anonymized: bool = True,
        **params: Any,
    ) -> Any:
        """
        Anonymizes the provided data (QuerySet, DjangoModel, or Schema) based on the user's permissions and the `anonymized` flag.

        Parameters:
            data (QuerySet | DjangoModel | Schema): The data to be anonymized. Can be a Django QuerySet, a Django model instance, or a Schema object.
            anonymized (bool, optional): If True, the data will be marked as anonymized. If False, checks if the user has permission to access non-anonymized data. Defaults to True.
            **params (Any): Additional parameters. Must include 'request' containing the HTTP request object.

        Returns:
            Any: The anonymized data, with an 'anonymized' attribute or annotation set to True if applicable.

        Raises:
            HttpError: If the 'request' parameter is missing or if the user lacks permission to access non-anonymized data.
        """
        request = params.get("request")
        if request is None:
            raise HttpError(400, "Request object is missing in parameters")
        user = request.user
        if not anonymized and not permissions.CanManageCases().check_user_permission(
            user
        ):
            raise HttpError(403, "Permission denied to access pseudonymized data")

        if anonymized:
            if isinstance(data, (DjangoModel, Schema)):
                setattr(data, "anonymized", True)
            elif isinstance(data, QuerySet):
                data = data.annotate(anonymized=Value(True))
            elif isinstance(data, (tuple, list)):
                for res in data:
                    setattr(res, "anonymized", True)
            else:
                pass
        return data


class AnonymizationOperation:
    """
    AnonymizationOperation is a decorator class that wraps a view function
    to apply anonymization logic to its output.

    This class is designed to integrate with a view function, intercept its output
    (typically a queryset), and apply an anonymization process before returning the result.
    It supports injecting anonymization parameters into the view function and ensures
    compatibility with frameworks that use request or controller objects.
    """

    def __init__(
        self,
        *,
        anonymization: AnonymizationBase,
        view_func: Callable,
        anonymization_kwargs_name: str = "anonymization",
    ) -> None:
        self.anonymization = anonymization
        self.anonymization_kwargs_name = anonymization_kwargs_name
        self.view_func = view_func

        anonymization_view = self.get_view_function()
        self.as_view = wraps(view_func)(anonymization_view)
        add_ninja_contribute_args(
            self.as_view,
            (
                self.anonymization_kwargs_name,
                self.anonymization.Input,
                self.anonymization.InputSource,
            ),
        )
        anonymization_view.anonymization_operation = self  # type:ignore[attr-defined]

    @property
    def view_func_has_kwargs(self) -> bool:  # pragma: no cover
        return self.anonymization.pass_parameter is not None

    def get_view_function(self) -> Callable:
        def as_view(
            request_or_controller: Union["ControllerBase", HttpRequest],  # type: ignore
            *args: Any,
            **kw: Any,
        ) -> Any:
            func_kwargs = dict(**kw)
            anonymization_params = func_kwargs.pop(self.anonymization_kwargs_name)
            if self.anonymization.pass_parameter:
                func_kwargs[self.anonymization.pass_parameter] = anonymization_params

            queryset = self.view_func(request_or_controller, *args, **func_kwargs)

            context = getattr(request_or_controller, "context", None)
            if context and isinstance(context, RouteContext):
                request = context.request
                assert request, "Request object is None"
            else:
                request = request_or_controller
            params = dict(kw)
            params["request"] = request
            return self.anonymization.anonymize_queryset(
                queryset, kw["anonymization"].anonymized, **params
            )

        return as_view


@overload
def anonymize() -> Callable[..., Any]:  # pragma: no cover
    ...


@overload
def anonymize(
    func_or_pgn_class: Any = NOT_SET, **anonymization_params: Any
) -> Callable[..., Any]:  # pragma: no cover
    ...


def anonymize(
    func_or_pgn_class: Any = NOT_SET, **anonymization_params: Any
) -> Callable[..., Any]:
    """
    Decorator to inject anonymization logic into a function or class.

    This decorator can be used without parameters: `@anonymize`

    Args:
        func_or_pgn_class (Any, optional): The function or class to be decorated. Defaults to NOT_SET.
        **anonymization_params (Any): Additional parameters for anonymization.

    Returns:
        Callable[..., Any]: The decorated function or class with anonymization logic applied.
    """
    isfunction = inspect.isfunction(func_or_pgn_class)
    is_not_set = func_or_pgn_class == NOT_SET

    if isfunction:
        return _inject_anonymization(func_or_pgn_class)

    def wrapper(func: Callable[..., Any]) -> Any:
        return _inject_anonymization(func, **anonymization_params)

    return wrapper


def _inject_anonymization(
    func: Callable[..., Any],
    **anonymization_params: Any,
) -> Callable[..., Any]:
    anonymization: AnonymizationBase = AnonymizationBase(**anonymization_params)
    anonymization_kwargs_name = "anonymization"
    anonymization_operation_class = AnonymizationOperation

    if is_async(func):
        raise NotImplementedError()
    anonymization_operation = anonymization_operation_class(
        anonymization=anonymization,
        view_func=func,
        anonymization_kwargs_name=anonymization_kwargs_name,
    )

    return anonymization_operation.as_view
