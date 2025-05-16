import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';

import { AppThemePreset } from './app.preset';
import { MessageService } from 'primeng/api';
import { DialogService } from 'primeng/dynamicdialog';

import { AuthInterceptor } from './core/auth/interceptors/auth.interceptor';
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { BASE_PATH } from './shared/openapi';
import { JDENTICON_CONFIG } from "ngx-jdenticon";
import { provideNgxCountAnimations } from "ngx-count-animation";
import {
    SocialAuthServiceConfig,
  } from '@abacritt/angularx-social-login';
  import { GoogleLoginProvider } from '@abacritt/angularx-social-login';
import { AuthErrorInterceptor } from './core/auth/interceptors/unauthorized.interceptor';
import { AppConfigService } from './app.config.service';


export const appConfig: ApplicationConfig = {
    providers: [
        AppConfigService,
        MessageService,
        DialogService,
        provideHttpClient(withInterceptorsFromDi()), 
        { 
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true,
        },
        { 
            provide: HTTP_INTERCEPTORS,
            useClass: AuthErrorInterceptor,
            multi: true,
        },
        provideZoneChangeDetection({ 
            eventCoalescing: true 
        }), 
        provideRouter(routes, withComponentInputBinding()),
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
        { provide: BASE_PATH, useValue: `${window.location.protocol}//${window.location.host}`},
        { provide: JDENTICON_CONFIG, useValue: {
            hues: [0, 0],
            lightness: {
                color: [0.21, 0.9],
                grayscale: [0.23, 0.62],
            },
            saturation: {
                color: 0.80,
                grayscale: 0.50,
            },
        }},
        provideNgxCountAnimations(),
        {
            provide: 'SocialAuthServiceConfig',
            useFactory: (configService: AppConfigService) => new Promise<void>((resolve) => {
                if (configService.isAuthConfigLoaded()) {
                    resolve();
                } else {
                    const checkInterval = setInterval(() => {
                        if (configService.isAuthConfigLoaded()) {
                        clearInterval(checkInterval);
                        resolve();
                        }
                    }, 50); // check every 50ms     
                }                
            }).then(() => ({
                autoLogin: false,
                providers: [
                    {
                    id: GoogleLoginProvider.PROVIDER_ID,
                    provider: new GoogleLoginProvider(configService.getIdentityProviderClientId('google') || '', {
                        oneTapEnabled: false
                    }),
                    },
                ],
                } as SocialAuthServiceConfig)
            ),
            deps: [AppConfigService]
        },
    ]
};
