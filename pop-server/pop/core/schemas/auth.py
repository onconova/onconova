from pydantic import ConfigDict, SecretStr
from ninja_jwt.schema import TokenObtainPairInputSchema, TokenObtainPairOutputSchema, TokenRefreshInputSchema, TokenRefreshOutputSchema

class UserCredentialsSchema(TokenObtainPairInputSchema):
    username: str
    password: SecretStr
    model_config = ConfigDict(title='UserCredentials')

class TokenPairSchema(TokenObtainPairOutputSchema):
    model_config = ConfigDict(title='TokenPair')

class TokenRefreshSchema(TokenRefreshInputSchema):
    model_config = ConfigDict(title='TokenRefresh')

class RefreshedTokenPairSchema(TokenRefreshOutputSchema):
    model_config = ConfigDict(title='RefreshedTokenPair')
