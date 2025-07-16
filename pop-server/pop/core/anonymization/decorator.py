import inspect
from abc import ABC
from functools import wraps
from typing import Any, Callable, Optional, Union, overload

from django.db.models import Model as DjangoModel
from django.db.models import QuerySet, Value
from django.http import HttpRequest
from ninja import Field, Query, Schema
from ninja.constants import NOT_SET
from ninja.errors import HttpError
from ninja.signature import is_async
from ninja_extra.controllers.route.context import RouteContext
from ninja_extra.shortcuts import add_ninja_contribute_args
from pop.core.auth import permissions


class AnonymizationBase(ABC):
    InputSource = Query(...)

    class Input(Schema):
        anonymized: bool = Field(
            default=True,
            title="Anonymize",
            description="Whether to anonymize the data or not (requires elevated permissions)",
        )

    def __init__(self, *, pass_parameter: Optional[str] = None, **kwargs: Any) -> None:
        self.pass_parameter = pass_parameter

    def anonymize_queryset(
        self,
        queryset: QuerySet,
        anonymized: bool = True,
        **params: Any,
    ) -> Any:
        user = params["request"].user
        if not anonymized and not permissions.CanManageCases().check_user_permission(
            user
        ):
            raise HttpError(403, "Permission denied to access pseudonymized data")

        if anonymized:
            if isinstance(queryset, (DjangoModel, Schema)):
                queryset.anonymized = True
            elif isinstance(queryset, (tuple, list)):
                for res in queryset:
                    res.anonymized = True
            else:
                queryset = queryset.annotate(anonymized=Value(True))
        return queryset


class AnonymizationOperation:
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

            if hasattr(request_or_controller, "context") and isinstance(
                request_or_controller.context, RouteContext
            ):
                request = request_or_controller.context.request
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
