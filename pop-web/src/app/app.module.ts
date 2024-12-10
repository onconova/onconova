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

import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import { AppThemePreset } from './app.preset'

// Messages imports 
import { ToastModule } from 'primeng/toast';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { InlineSVGModule } from 'ng-inline-svg-2';

import { LucideAngularModule, HeartPulse, Tags, 
    TestTubeDiagonal, Dna, Fingerprint, Microscope,
    Siren, DiamondPlus, Activity, Cigarette, Tablets, 
    Slice, Radiation, Ribbon, Presentation, ShieldAlert,
    Image, CircleGauge} from 'lucide-angular';




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
        InlineSVGModule.forRoot(),
        LucideAngularModule.pick({HeartPulse, Tags, TestTubeDiagonal, Dna, Fingerprint, Microscope, Siren, DiamondPlus, Activity, Cigarette, Tablets, Slice, Radiation, Ribbon, Presentation, ShieldAlert, Image, CircleGauge}),
    ],
    providers: [
        provideAnimationsAsync(),
        providePrimeNG({ 
            ripple: true,
            theme: {
                preset: AppThemePreset,
                options: {
                    darkModeSelector: '.dark-mode'
                }
            }
        }),
        { provide: LocationStrategy, useClass: HashLocationStrategy },
        { provide: BASE_PATH, useValue: 'https://localhost:4443' },
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
        { provide: CACHE_OPTIONS, useValue: { /* options */ } },
        { provide: HTTP_INTERCEPTORS, useClass: HttpCacheInterceptor, multi: true },
        AuthGuard
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
