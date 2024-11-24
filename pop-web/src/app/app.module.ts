import { APP_INITIALIZER, NgModule } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppComponent } from './app.component';
import { BASE_PATH } from './openapi/variables';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './notfound/notfound.component';
import { AuthInterceptor } from './auth/auth.interceptor';
import { ApiModule, Configuration, ConfigurationParameters } from './openapi/';
import { AuthGuard } from './auth/auth.guard';
import { PrimeNGConfig } from 'primeng/api';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


const initializeAppFactory = (primeConfig: PrimeNGConfig) => () => {
    primeConfig.ripple = true;
};


export function apiConfigFactory (): Configuration {
    const params: ConfigurationParameters = {
      // set configuration parameters here.
    }
    return new Configuration(params);
}

@NgModule({
    declarations: [
        AppComponent, NotfoundComponent
    ],
    imports: [
        AppRoutingModule,
        AppLayoutModule,
        ApiModule.forRoot(apiConfigFactory),
        FormsModule, 
        ReactiveFormsModule,
    ],
    providers: [
        { provide: LocationStrategy, useClass: HashLocationStrategy },
        { provide: BASE_PATH, useValue: 'https://localhost:4443' },
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
        {
            provide: APP_INITIALIZER,
            useFactory: initializeAppFactory,
            deps: [PrimeNGConfig],
            multi: true,
         },
        // { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
        AuthGuard
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
