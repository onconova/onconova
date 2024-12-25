import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';

import { AppThemePreset } from './app.preset';

import { httpCacheInterceptor } from './core/interceptors/cache.interceptor';
import { authInterceptor } from './auth/auth.interceptor';
import { AuthGuard } from './auth/auth.guard';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { BASE_PATH } from './core/modules/openapi';


export const appConfig: ApplicationConfig = {
    providers: [
        provideZoneChangeDetection({ 
            eventCoalescing: true 
        }), 
        provideRouter(routes),
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
        provideHttpClient(
            withInterceptors([
                authInterceptor, 
                httpCacheInterceptor
            ]),
        ),
        { provide: BASE_PATH, useValue: 'https://localhost:4443' },
    ]
};
