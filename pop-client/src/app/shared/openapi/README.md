# @

 Welcome to the Precision Oncology Platform API — a secure, standards-based interface designed to facilitate the exchange, management, and  analysis of research data related to cancer genomics, clinical records, and associated metadata. This API provides an extensive set of  RESTful endpoints enabling authorized users to perform full CRUD (Create, Read, Update, Delete) operations on various resources within the platform’s data ecosystem.  The primary objective of this API is to support precision oncology research by enabling interoperability between data systems,  promoting data sharing among research institutions, and streamlining workflows for clinical and genomic data management in a secure, authenticated environment.  ### Authentication To ensure the security and integrity of cancer research data, **all API requests require proper authentication**.  A valid session token must be obtained prior to accessing any protected endpoint. This token must be included in the request header `X-Session-Token`.  The authentication and authorization flows for obtaining and managing session tokens are provided through the AllAuth authentication service.  This includes endpoints for user login, logout, password management, and token renewal. For complete details on implementing authentication and  managing session tokens, please refer to the [AllAuth API documentation](/api/allauth/openapi.html).  **Important:** Unauthorized requests or those missing valid authentication tokens will receive an `HTTP 401 Unauthorized` response.  ### Terms and Conditions By accessing and using this website, you agree to comply with and be bound by the following terms and conditions. The content provided on this API is  intended solely for general informational and research purposes. While we strive to ensure the information is accurate and reliable, we do not make  any express or implied warranties about the accuracy, adequacy, validity, reliability, availability, or completeness of the content.  The information presented on this platform is provided in good faith. However, we do not accept any liability for any loss or damage incurred as a  result of using the site or relying on the information provided. Your use of this site and any reliance on the content is solely at your own risk.  These terms and conditions may be updated from time to time, and it is your responsibility to review them regularly to ensure compliance.  ### License  This API is made available under the MIT License.     

The version of the OpenAPI document: 1.0.0

## Building

To install the required dependencies and to build the typescript sources run:

```console
npm install
npm run build
```

## Publishing

First build the package then run `npm publish dist` (don't forget to specify the `dist` folder!)

## Consuming

Navigate to the folder of your consuming project and run one of next commands.

_published:_

```console
npm install @ --save
```

_without publishing (not recommended):_

```console
npm install PATH_TO_GENERATED_PACKAGE/dist.tgz --save
```

_It's important to take the tgz file, otherwise you'll get trouble with links on windows_

_using `npm link`:_

In PATH_TO_GENERATED_PACKAGE/dist:

```console
npm link
```

In your project:

```console
npm link 
```

__Note for Windows users:__ The Angular CLI has troubles to use linked npm packages.
Please refer to this issue <https://github.com/angular/angular-cli/issues/8284> for a solution / workaround.
Published packages are not effected by this issue.

### General usage

In your Angular project:

```typescript
// without configuring providers
import { ApiModule } from '';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
    imports: [
        ApiModule,
        // make sure to import the HttpClientModule in the AppModule only,
        // see https://github.com/angular/angular/issues/20575
        HttpClientModule
    ],
    declarations: [ AppComponent ],
    providers: [],
    bootstrap: [ AppComponent ]
})
export class AppModule {}
```

```typescript
// configuring providers
import { ApiModule, Configuration, ConfigurationParameters } from '';

export function apiConfigFactory (): Configuration {
  const params: ConfigurationParameters = {
    // set configuration parameters here.
  }
  return new Configuration(params);
}

@NgModule({
    imports: [ ApiModule.forRoot(apiConfigFactory) ],
    declarations: [ AppComponent ],
    providers: [],
    bootstrap: [ AppComponent ]
})
export class AppModule {}
```

```typescript
// configuring providers with an authentication service that manages your access tokens
import { ApiModule, Configuration } from '';

@NgModule({
    imports: [ ApiModule ],
    declarations: [ AppComponent ],
    providers: [
      {
        provide: Configuration,
        useFactory: (authService: AuthService) => new Configuration(
          {
            basePath: environment.apiUrl,
            accessToken: authService.getAccessToken.bind(authService)
          }
        ),
        deps: [AuthService],
        multi: false
      }
    ],
    bootstrap: [ AppComponent ]
})
export class AppModule {}
```

```typescript
import { DefaultApi } from '';

export class AppComponent {
    constructor(private apiGateway: DefaultApi) { }
}
```

Note: The ApiModule is restricted to being instantiated once app wide.
This is to ensure that all services are treated as singletons.

### Using multiple OpenAPI files / APIs / ApiModules

In order to use multiple `ApiModules` generated from different OpenAPI files,
you can create an alias name when importing the modules
in order to avoid naming conflicts:

```typescript
import { ApiModule } from 'my-api-path';
import { ApiModule as OtherApiModule } from 'my-other-api-path';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    ApiModule,
    OtherApiModule,
    // make sure to import the HttpClientModule in the AppModule only,
    // see https://github.com/angular/angular/issues/20575
    HttpClientModule
  ]
})
export class AppModule {

}
```

### Set service base path

If different than the generated base path, during app bootstrap, you can provide the base path to your service.

```typescript
import { BASE_PATH } from '';

bootstrap(AppComponent, [
    { provide: BASE_PATH, useValue: 'https://your-web-service.com' },
]);
```

or

```typescript
import { BASE_PATH } from '';

@NgModule({
    imports: [],
    declarations: [ AppComponent ],
    providers: [ provide: BASE_PATH, useValue: 'https://your-web-service.com' ],
    bootstrap: [ AppComponent ]
})
export class AppModule {}
```

### Using @angular/cli

First extend your `src/environments/*.ts` files by adding the corresponding base path:

```typescript
export const environment = {
  production: false,
  API_BASE_PATH: 'http://127.0.0.1:8080'
};
```

In the src/app/app.module.ts:

```typescript
import { BASE_PATH } from '';
import { environment } from '../environments/environment';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [ ],
  providers: [{ provide: BASE_PATH, useValue: environment.API_BASE_PATH }],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
```

### Customizing path parameter encoding

Without further customization, only [path-parameters][parameter-locations-url] of [style][style-values-url] 'simple'
and Dates for format 'date-time' are encoded correctly.

Other styles (e.g. "matrix") are not that easy to encode
and thus are best delegated to other libraries (e.g.: [@honoluluhenk/http-param-expander]).

To implement your own parameter encoding (or call another library),
pass an arrow-function or method-reference to the `encodeParam` property of the Configuration-object
(see [General Usage](#general-usage) above).

Example value for use in your Configuration-Provider:

```typescript
new Configuration({
    encodeParam: (param: Param) => myFancyParamEncoder(param),
})
```

[parameter-locations-url]: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-locations
[style-values-url]: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#style-values
[@honoluluhenk/http-param-expander]: https://www.npmjs.com/package/@honoluluhenk/http-param-expander
