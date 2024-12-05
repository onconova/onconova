import { APP_INITIALIZER, NgModule } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS, provideHttpClient, withInterceptors } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './notfound/notfound.component';
import { ApiModule, Configuration, ConfigurationParameters } from './core/modules/openapi/';

import { HttpCacheInterceptor, CACHE_OPTIONS } from './core/interceptors/cache.interceptor';
import { AuthInterceptor } from './auth/auth.interceptor';
import { AuthGuard } from './auth/auth.guard';

import { BASE_PATH } from './core/modules/openapi/variables';
import { PrimeNGConfig } from 'primeng/api';

// Messages imports 
import { ToastModule } from 'primeng/toast';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { CaseBrowserModule } from './case-browser/case-browser.module';
import { CaseManagerModule } from './case-manager/case-manager.module';

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
        CaseBrowserModule,
        CaseManagerModule,
    ],
    providers: [
        
        { provide: LocationStrategy, useClass: HashLocationStrategy },
        { provide: BASE_PATH, useValue: 'https://localhost:4443' },
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
        { provide: CACHE_OPTIONS, useValue: { /* options */ } },
        { provide: HTTP_INTERCEPTORS, useClass: HttpCacheInterceptor, multi: true },
        {
            provide: APP_INITIALIZER,
            useFactory: initializeAppFactory,
            deps: [PrimeNGConfig],
            multi: true,
         },
        AuthGuard
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
