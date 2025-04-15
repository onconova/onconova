import { Injectable, signal, effect, computed, WritableSignal, Signal } from '@angular/core';
import { Subject } from 'rxjs';
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

interface LayoutState {
    staticMenuDesktopInactive: boolean;
    overlayMenuActive: boolean;
    profileSidebarVisible: boolean;
    configSidebarVisible: boolean;
    staticMenuMobileActive: boolean;
    menuHoverActive: boolean;
}

@Injectable({
    providedIn: 'root',
})
export class LayoutService {

    public config: AppConfig = {
        ripple: true,
        inputStyle: 'outlined',
        menuMode: 'static',
        darkMode: signal(false),
        theme: signal('blue'),
        scale: 14,
    };

    public state: LayoutState = {
        staticMenuDesktopInactive: false,
        overlayMenuActive: false,
        profileSidebarVisible: false,
        configSidebarVisible: false,
        staticMenuMobileActive: false,
        menuHoverActive: false
        
    };

    public readonly logo: string = 'assets/images/logo-dark.svg';

    private configUpdate = new Subject<AppConfig>();
    private overlayOpen = new Subject<any>();
    public configUpdate$ = this.configUpdate.asObservable();
    public overlayOpen$ = this.overlayOpen.asObservable();

    constructor() {
        // Load user preferences from local storage
        this.getUserPreferences()
        // Upon any change, store new preferences in local storage 
        effect(() => {
            localStorage.setItem('pop-layout-config-darkMode', this.config.darkMode().toString())
            localStorage.setItem('pop-layout-config-theme', this.config.theme().toString())
        });
        effect( () => {
            this.updateDarkMode()
        });
        effect( () => {
            this.updateTheme()
        });
    }

    onMenuToggle() {
        if (this.isOverlay()) {
            this.state.overlayMenuActive = !this.state.overlayMenuActive;
            if (this.state.overlayMenuActive) {
                this.overlayOpen.next(null);
            }
        }

        if (this.isDesktop()) {
            this.state.staticMenuDesktopInactive = !this.state.staticMenuDesktopInactive;
        }
        else {
            this.state.staticMenuMobileActive = !this.state.staticMenuMobileActive;

            if (this.state.staticMenuMobileActive) {
                this.overlayOpen.next(null);
            }
        }
    }

    getUserPreferences() {
        const darkModePreference = localStorage.getItem('pop-layout-config-darkMode');
        if (darkModePreference) {
            this.config.darkMode.set(darkModePreference.toLowerCase() === 'true');
        }
        const themePreference = localStorage.getItem('pop-layout-config-theme');
        if (themePreference) {
            this.config.theme.set(themePreference);
        }
    }

    toggleDarkMode() {
        this.config.darkMode.set(!this.config.darkMode());
    }

    updateDarkMode() {
        const element = document.querySelector('html');
        const darkModeSetting: boolean = this.config.darkMode()
        if (element) {
            element.classList.toggle('dark-mode', darkModeSetting);
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
        updatePreset(
            {
            semantic: {
                colorScheme: {
                    light: {
                        primary: scheme
                    },
                    dark: {
                        primary: scheme
                    }
                }
            }
        })
    }

    showProfileSidebar() {
        this.state.profileSidebarVisible = !this.state.profileSidebarVisible;
        if (this.state.profileSidebarVisible) {
            this.overlayOpen.next(null);
        }
    }

    showConfigSidebar() {
        this.state.configSidebarVisible = true;
    }

    isOverlay() {
        return this.config.menuMode === 'overlay';
    }

    isDarkMode() {
        return this.config.darkMode;
    }

    isDesktop() {
        return window.innerWidth > 991;
    }

    isMobile() {
        return !this.isDesktop();
    }

    onConfigUpdate() {
        this.configUpdate.next(this.config);
        // localStorage.setItem('darkMode', element.classList.contains('dark-mode').toString());
    }

}
