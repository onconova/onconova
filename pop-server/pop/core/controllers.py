from datetime import datetime

from ninja_extra import route, api_controller
from ninja_extra.exceptions import APIException
from ninja_extra import status
from ninja_jwt import schema
from ninja_jwt.controller import TokenObtainSlidingController
from ninja_jwt.tokens import SlidingToken

from pop.core.schemas import UserSchema, UserTokenSchema


@api_controller("/auth", tags=["Auth"])
class AuthController(TokenObtainSlidingController):
    @route.post("/login", response=UserTokenSchema)
    def login(self, user_token: schema.TokenObtainSlidingInputSchema):
        user = user_token._user
        token = SlidingToken.for_user(user)

        return UserTokenSchema(
            token=str(token),
            user=user,
            token_exp_date=datetime.fromtimestamp(token["exp"]),
        )
    