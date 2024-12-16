from datetime import datetime

from ninja_extra import route, api_controller, ControllerBase
from ninja_jwt.controller import TokenObtainPairController
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import AccessToken, RefreshToken

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from typing import List 


from pop.core.schemas import (
    UserSchema, 
    TokenRefreshSchema, 
    RefreshedTokenPairSchema,
    TokenPairSchema, 
    UserCredentialsSchema
)
from measurement.base import MeasureBase, BidimensionalMeasure
from pop.core.schemas import MeasureConversionSchema, MeasureSchema
import pop.core.measures as measures


@api_controller(
    "/auth/token", 
    tags=["Auth"]
)
class AuthController(ControllerBase):

    @route.post(
        "/pair",
        response=TokenPairSchema,
        url_name="token_obtain_sliding",
        operation_id="getSlidingToken",
    )
    def obtain_token_pair(self, credentials: UserCredentialsSchema):
        credentials.check_user_authentication_rule()
        return credentials.to_response_schema()

    @route.post(
        "/refresh",
        response=RefreshedTokenPairSchema,
        url_name="token_refresh_sliding",
        operation_id="refereshSlidingToken",
    )
    def refresh_token_pair(self, refresh_token: TokenRefreshSchema):
        return refresh_token.to_response_schema()
    
    
@api_controller(
    '/auth', 
    auth=[JWTAuth()], 
    tags=['Auth'],  
)
class UsersController(ControllerBase):

    @route.get(
        path="/users",
        operation_id='getUsers',
        response={
            200: List[UserSchema]
        }, 
    )
    def get_all_users_matching_the_query(self):
        return get_user_model().objects.all()
    
    @route.get(
        path="/users/{userId}", 
        operation_id='getUserById',
        response={
            200: UserSchema,
            404: None
        }, 
    )
    def get_user_by_id(self, userId: int):
        return get_object_or_404(get_user_model(), id=userId)



    
@api_controller(
    '/measures', 
    # auth=[JWTAuth()], 
    tags=['Measures'],  
)
class MeasuresController(ControllerBase):

    @route.get(
        path="/{measureName}/units", 
        operation_id='getMeasureUnits',
        response={
            200: List[str],
            404: None
        }, 
    )
    def get_measure_units(self, measureName: str):
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        units = []
        if issubclass(measure, MeasureBase):
            units = list(measure.UNITS.keys())
        elif issubclass(measure, BidimensionalMeasure):
            primaries = list(measure.PRIMARY_DIMENSION.UNITS.keys())
            references = list(measure.REFERENCE_DIMENSION.UNITS.keys())
            units = [
                f'{primary}__{reference}' for primary in primaries for reference in references
            ]
        return 200, units

    @route.get(
        path="/{measureName}/units/default", 
        operation_id='getMeasureDefaultUnits',
        response={
            200: str,
            404: None
        }, 
    )
    def get_measure_default_units(self, measureName: str):
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        return 200, measure.STANDARD_UNIT


    @route.post(
        path="/{measureName}/units/conversion", 
        operation_id='convertUnits',
        response={
            200: MeasureSchema,
            404: None
        }, 
    )
    def convert_units(self, measureName: str, payload: MeasureConversionSchema):
        measureClass = getattr(measures, measureName, None)
        if measureClass is None:
            return 404, None
        measure = measureClass(**{payload.unit: payload.value})
        converted_value = getattr(measure, payload.new_unit)
        return 200, MeasureSchema(unit=payload.new_unit, value=converted_value)