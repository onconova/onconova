import { APP_INITIALIZER, NgModule } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './notfound/notfound.component';
import { AuthInterceptor } from './auth/auth.interceptor';
import { ApiModule, Configuration, ConfigurationParameters } from './core/modules/openapi/';
import { BASE_PATH } from './core/modules/openapi/variables';
import { AuthGuard } from './auth/auth.guard';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { PrimeNGConfig } from 'primeng/api';

// Messages imports 
import { ToastModule } from 'primeng/toast';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

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
        BrowserAnimationsModule,
        ToastModule,
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
