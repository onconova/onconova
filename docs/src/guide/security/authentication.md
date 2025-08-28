This project implements secure and flexible authentication practices for both traditional and OpenID Connect (OIDC) Single Sign-On (SSO) workflows. The backend integrates the excellent [Django-AllAuth](https://django-allauth.readthedocs.io/en/latest/) package to handle user registration, login, password management, and third-party authentication providers.

## Authentication Method

All API endpoints in Onconova require a valid, authenticated user session. Authentication is managed via a session token, which must be included in the `X-SESSION-TOKEN` HTTP header for every request.

A session token is issued by *Django-AllAuth* upon successful user authentication, whether through traditional username/email+password sign-in or supported Single Sign-On (SSO) providers. Requests that lack a valid session token, or include an expired or invalid token, will receive a `401 Unauthorized` HTTP response.

!!! important "Authorized users only" 

    Onconova does not support anonymous or unauthenticated API access.

#### How to Authenticate

=== "Username/password Sign-in"

    1. Obtain a session token by logging in through the web interface or by using the API login endpoint:
        ```
        POST /api/v1/auth/session
        ```

        Example JSON body:
        ```json
        {
            "username": "admin",
            "password": "your_password"
        }
        ```

        Example response:
        ```json
        {
            "sessionToken": "eyJ0eXAiOiJKV1QiLCJh...",
            "accessToken": "...",
            "isAuthenticated": true
        }
        ```

    2. Include the `sessionToken` value in the `X-SESSION-TOKEN` header in your subsequent API requests.

        Example Request with Token:
        ```bash
        curl -X GET "https://onconova.example.com/api/patients/" \
            -H "X-SESSION-TOKEN: eyJ0eXAiOiJKV1QiLCJh..."
        ```


=== "OIDC Access or ID Token"

    1. Provide your credentials to your provider's OIDC authorization endpoint and follow their OIDC flow to obtain either an `id_token` or `access_token` value.
        Example request:
        ```
        GET https://accounts.google.com/o/oauth2/v2/auth?...
        ```

        Example response:
        ```json
        {
            "id_token": "apJ2eXA52OivGlaKV1QiLC...",
        }
        ```

    2. Obtain a session token by providing the `id_token` or `access_token` value, as well as other provider details, to the Onconova API interface:
        ```
        POST /api/v1/auth/provider/session
        ```

        Example JSON body:
        ```json
        {
            "provider": "google",
            "token": {
                "client_id": "123.apps.googleusercontent.com",
                "id_token": "apJ2eXA52OivGlaKV1QiLC...",
                "access_token": "..."
            }
        }
        ```

        Example response:
        ```json
        {
            "sessionToken": "eyJ0eXAiOiJKV1QiLCJh...",
            "accessToken": "...",
            "isAuthenticated": true
        }
        ```

    3. Include the `sessionToken` value in the `X-SESSION-TOKEN` header in your subsequent API requests.

        Example Request with Token:
        ```bash
        curl -X GET "https://onconova.example.com/api/patients/" \
            -H "X-SESSION-TOKEN: eyJ0eXAiOiJKV1QiLCJh..."
        ```




!!! note "Token Expiration"
    
    Tokens are valid for a limited period or until manually revoked. After the expriration period, users must authenticate again to retrieve a new token.

!!! warning "Security Considerations"

    - Always keep your session tokens secure.
    - Never expose API credentials or tokens in public code repositories.
    - Use HTTPS connections for all API calls. HTTP connections will be redirected to HTTPS by default.


## SSO through Identity Providers

The project currently supports the following OIDC identity providers:

- Google
- Microsoft

Both are integrated using Django-AllAuth’s social account providers. To enable SSO with a specific identity provider, the Onconova application **must first be registered with the provider** to define access permissions, data scope, and user consent options. Upon successful registration, the provider will issue an **Application (client) ID** and a **Client Secret**. These credentials, along with any additional provider-specific configuration parameters, are required by Onconova to establish and manage the OIDC authentication workflow.

!!! important "Supported OIDC Flows"

    The Onconova client currently supports OIDC authentication using **ID tokens** and **Access tokens**. The *Authorization Code* flow (involving the exchange of authorization codes) is **not supported**.

!!! note "Client-only"

    OIDC authentication is enabled exclusively for client-side authentication in Onconova. API requests must be authenticated either via a traditional login or with an OIDC access token. Importantly, no provider credentials are uploaded to or stored within the Onconova server, identity verification is handled entirely through the client’s interaction with the identity provider.



### Google

To enable Google SSO:

1. Go to your organization's [Google Cloud Console](https://console.cloud.google.com/) and navigate to the *APIs and services* page.  

2. Create an new **OAuth 2.0 Client ID**

    - Under *Application type* select **Web application**.
    - Add your Onconova domain to *Authorised JavaScript origins*.
    - Add the Onconova `/auth/callback` URL under *Authorized redirect URLs*:
        ```url
        https://your-onconova-domain/auth/callback
        ```
3. Create a **Client Secret**.

4. Assign the Google **Client ID** to the `ONCONOVA_GOOGLE_CLIENT_ID` variable and the **Client Secret** to the `ONCONOVA_GOOGLE_SECRET` variable in the `.env` file. 
    ```.env
    ONCONOVA_GOOGLE_CLIENT_ID='694913361-005t3059...'
    ONCONOVA_GOOGLE_SECRET='GOSFICPX-Iqr46NgX5...'
    ```


### Microsoft

To enable Microsoft SSO through ID tokens:

1. Go to your organization's [Microsoft Entra admin center](https://entra.microsoft.com/) and navigate to the *APIs and services* page.  

2. Browse to Entra ID > App registrations > Onconova > Authentication.

3. Under *Platform configurations*, select *Add a platform*. In the pane that opens, select **Web** for a web application.

4. Under *Redirect URIs*, add the Onconova `/auth/callback` redirect URL:
    ```url
    https://your-onconova-domain/auth/callback
    ```

5. Under *Implicit grant and hybrid flows*, select the **ID tokens** checkbox.

4. Assign the Microsoft **Client ID** to the `ONCONOVA_MICROSOFT_CLIENT_ID` variable, the **Client Secret** to the `ONCONOVA_MICROSOFT_SECRET` variable, and the **Tenant ID** to the `ONCONOVA_MICROSOFT_TENANT_ID` variable in the `.env` file. 
    ```.env
    ONCONOVA_MICROSOFT_CLIENT_ID='694913361-005t3059...'
    ONCONOVA_MICROSOFT_SECRET='GOSFICPX-Iqr46NgX5...'
    ONCONOVA_MICROSOFT_TENANT_ID='16841664...'
    ```

## Further reading

- [Django-AllAuth homepage](https://allauth.org/)
- [OpenID Connect on Google Cloud](https://developers.google.com/identity/openid-connect/openid-connect)
- [OpenID Connect on the Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)