import { Injectable, signal, effect, computed, WritableSignal } from '@angular/core';
import { updatePreset } from '@primeng/themes';
import { AppThemes } from 'src/app/app.preset';

export interface AppConfig {
    inputStyle: string;
    darkMode: WritableSignal<boolean>;
    theme: WritableSignal<string>;
    ripple: boolean;
    menuMode: string;
    scale: number;
}


@Injectable({
    providedIn: 'root',
})
export class LayoutService {

    private static readonly STORAGE_KEYS = {
        darkMode: 'onconova-layout-config-darkMode',
        theme: 'onconova-layout-config-theme'
    };

    public config: AppConfig = {
        ripple: true,
        inputStyle: 'outlined',
        menuMode: 'static',
        darkMode: signal(false),
        theme: signal('blue'),
        scale: 14,
    };

    // State as signals
    isStaticMenuDesktopInactive = signal(false);
    isOverlayMenuActive = signal(false);
    isProfileSidebarVisible = signal(false);
    isConfigSidebarVisible = signal(false);
    isStaticMenuMobileActive = signal(false);
    isMenuHoverActive = signal(false);
    windowWidth = signal(window.innerWidth);
    
    // Computed properties
    isOverlayMode = computed(() => this.config.menuMode === 'overlay');
    isDarkMode = computed(() => this.config.darkMode());
    isDesktop = computed(() => this.windowWidth() > 991);
    isMobile = computed(() => !this.isDesktop());


    // Simple trigger signal for overlay open event
    #overlayOpenTrigger = signal(0);
    overlayOpenSignal = computed(() => this.#overlayOpenTrigger());

    public readonly logo: string = 'assets/images/logo.svg';

    constructor() {
        // Load user preferences from local storage
        this.getStoredUserPreferences()
        // Upon any change, store new preferences in local storage 
        effect(() => {
            localStorage.setItem('onconova-layout-config-darkMode', this.config.darkMode().toString())
            localStorage.setItem('onconova-layout-config-theme', this.config.theme().toString())
        });
        effect( () => this.updateDarkMode());
        effect( () => this.updateTheme());
        window.addEventListener('resize', () => this.windowWidth.set(window.innerWidth));
    }

    onMenuToggle() {
        if (this.isOverlayMode()) {
            this.isOverlayMenuActive.update(value => !value);
            if (this.isOverlayMenuActive()) this.triggerOverlayOpen();
        }

        if (this.isDesktop()) {
            this.isStaticMenuDesktopInactive.update(value => !value);
        }
        else {
            this.isStaticMenuMobileActive.update(value => !value);
            if (this.isStaticMenuMobileActive()) this.triggerOverlayOpen();
        }
    }

    getStoredUserPreferences() {
        const darkModePreference = localStorage.getItem(LayoutService.STORAGE_KEYS.darkMode);
        if (darkModePreference) {
            this.config.darkMode.set(darkModePreference.toLowerCase() === 'true');
        }
        const themePreference = localStorage.getItem(LayoutService.STORAGE_KEYS.theme);
        if (themePreference) {
            this.config.theme.set(themePreference);
        }
    }

    toggleDarkMode() {
        this.config.darkMode.update(value => !value);
    }

    updateDarkMode() {
        const element = document.querySelector('html');
        if (element) {
            element.classList.toggle('dark-mode', this.config.darkMode());
        }
    }

    updateTheme() {
        const theme = this.config.theme()
        const element = document.querySelector('html');
        if (element) {
            // Remove any class that starts with 'layout-theme-' and add the new theme class
            Array.from(element.classList)
                 .filter(cls => cls.startsWith('layout-theme-'))
                 .forEach(cls => element.classList.remove(cls));
            element.classList.add(`layout-theme-${theme}`);
        }
        const scheme = AppThemes[theme as keyof typeof AppThemes];
        updatePreset({
            semantic: {
                colorScheme: {
                    light: {primary: scheme},
                    dark: {primary: scheme}
                },
            },
        });
    }

    showProfileSidebar() {
        this.isProfileSidebarVisible.update(value => !value);
        if (this.isProfileSidebarVisible()) this.triggerOverlayOpen();
    }

    showConfigSidebar() {
        this.isConfigSidebarVisible.set(true);
    }

    private triggerOverlayOpen() {
        this.#overlayOpenTrigger.update(v => v + 1);
    }

}
