from pydantic import SecretStr
from ninja_jwt.schema import TokenObtainPairInputSchema, TokenObtainPairOutputSchema, TokenRefreshInputSchema, TokenRefreshOutputSchema

class UserCredentials(TokenObtainPairInputSchema):
    username: str
    password: SecretStr

class TokenPair(TokenObtainPairOutputSchema): pass
class TokenRefresh(TokenRefreshInputSchema): pass
class RefreshedTokenPair(TokenRefreshOutputSchema): pass
