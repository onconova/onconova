import { computed, Injectable, signal } from '@angular/core';
import { AllAuthApiService, AllAuthConfiguration, ProviderConfig } from './core/auth/allauth-api.service';
import { catchError, firstValueFrom, map, of, tap } from 'rxjs';
import { rxResource } from '@angular/core/rxjs-interop';

@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
    constructor(private allauthService: AllAuthApiService) {}

    #authConfig = rxResource({
        request: () => ({}),
        loader: () => this.allauthService.getConfig()
    })
    public isAuthConfigLoaded = computed(() => this.#authConfig.hasValue())

    public getIdentityProviders() {
        return this.#authConfig.value()?.socialaccount?.providers || []
    }

    public getIdentityProviderClientId(providerId: string): string | null {
        return this.getIdentityProviders().find((provider: ProviderConfig) => provider.id == providerId)?.client_id || null;
    }

    public getAllowedLoginMethds(): string[] {
        return this.#authConfig.value()?.account.login_methods || []
    }
}