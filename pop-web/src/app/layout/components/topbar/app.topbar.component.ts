import { Component, ElementRef, ViewChild } from '@angular/core';
import { MessageService } from 'primeng/api';
import { LayoutService } from "../../service/app.layout.service";
import packageInfo from '../../../../../package.json';
import { AuthService } from '../../../auth/auth.service';
import { Router } from '@angular/router';
import { updatePreset } from '@primeng/themes';

@Component({
    selector: 'app-topbar',
    templateUrl: './app.topbar.component.html',
    providers: [MessageService]
})
export class AppTopBarComponent {
    version = packageInfo.version;
    items!: any[];
    profile_items!: any[];
    themeModeIcon: 'pi pi-sun' | 'pi pi-moon' = 'pi pi-sun';


    @ViewChild('menubutton') menuButton!: ElementRef;

    @ViewChild('topbarmenubutton') topbarMenuButton!: ElementRef;

    @ViewChild('topbarmenu') menu!: ElementRef;

    constructor(
        public layoutService: LayoutService,
        private router: Router,
        private messageService: MessageService,
        public authService: AuthService) { 

        this.profile_items = [
            {
                separator: true
            },
            {
                label: 'Profile',
                items: [
                    {
                        label: 'Palette',
                        icon: 'pi pi-pencil',
                        command: () => {
                            this.changePrimaryColor();
                        }
                    },
                    {
                        label: 'Logout',
                        icon: 'pi pi-file',
                        command: () => {
                            this.logout();
                        }
                    },
                ]
            },
        ];
    }


    ngOnInit(): void {
        const darkModePreference = localStorage.getItem('darkMode');
        if (darkModePreference === 'true') {
            this.themeModeIcon = 'pi pi-moon';
            const element = document.querySelector('html');
            if (element) {
                element.classList.add('dark-mode');
            }
        } else {
            this.themeModeIcon = 'pi pi-sun';
        }
    }

    toggleDarkMode() {
        const element = document.querySelector('html');
        if (element) {
            this.themeModeIcon = this.themeModeIcon == 'pi pi-moon' ? 'pi pi-sun' : 'pi pi-moon'
            element.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', element.classList.contains('dark-mode').toString());
        }
    }


    
    changePrimaryColor() {
        const element = document.querySelector('html');
        if (element) {
            element.classList.toggle('teal-theme');
        }
        const scheme = {
            50: '{teal.50}',
            100: '{teal.100}',
            200: '{teal.200}',
            300: '{teal.300}',
            400: '{teal.400}',
            500: '{teal.500}',
            600: '{teal.600}',
            700: '{teal.700}',
            800: '{teal.800}',
            900: '{teal.900}',
            950: '{teal.950}'
        }
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

    logout() {
        this.authService.logout()
        this.router.navigate(['login'])
        this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Succesful logout' });
    }
    
}
