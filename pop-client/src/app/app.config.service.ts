import { computed, inject, Injectable, signal } from '@angular/core';
import { AllAuthApiService, AllAuthConfiguration, ProviderConfig } from './core/auth/services/allauth-api.service';
import { catchError, firstValueFrom, map, Observable, of, tap, throwError } from 'rxjs';
import { rxResource } from '@angular/core/rxjs-interop';
import { BASE_PATH } from 'pop-api-client';
import { HttpClient } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
    
    #allauthService = inject(AllAuthApiService);
    #http =  inject(HttpClient);

    public BASE_PATH = inject(BASE_PATH)
    #authConfigResource = rxResource({
        request: () => ({}),
        loader: () => this.#allauthService.getConfig()
    })
    public isAuthConfigLoaded = computed(() => this.#authConfigResource.hasValue())
    public authConfig = computed<AllAuthConfiguration>(() => this.#authConfigResource.value()!)

    public getIdentityProviders() {
        return (this.authConfig()?.socialaccount?.providers || []).filter(provider => provider.client_id != null);
    }

    public getIdentityProviderClientId(providerId: string): string | null {
        return this.getIdentityProviders().find((provider: ProviderConfig) => provider.id == providerId)?.client_id || null;
    }

    public getAllowedLoginMethds(): string[] {
        return this.authConfig()?.account.login_methods || []
    }
    public getOpenIdAuthorizationEndpoint(providerId: string): Observable<string | null> {
        const configUrl: string | null = this.getIdentityProviders().find((provider: ProviderConfig) => provider.id == providerId)?.openid_configuration_url || null;
        if (!configUrl) return of(null);
        return this.#http.get(configUrl).pipe(
            map((config: any) => config.authorization_endpoint),
            catchError((error) => throwError(() => 'Failed to fetch OpenID configuration for ' + providerId + ': ' + error))
        )
    }
    public getOpenIdTokenEndpoint(providerId: string): Observable<string | null> {
        const configUrl: string | null = this.getIdentityProviders().find((provider: ProviderConfig) => provider.id == providerId)?.openid_configuration_url || null;
        if (!configUrl) return of(null);
        return this.#http.get(configUrl).pipe(
            map((config: any) => config.token_endpoint),
            catchError((error) => throwError(() => 'Failed to fetch OpenID configuration for ' + providerId + ': ' + error))
        )
    }
}