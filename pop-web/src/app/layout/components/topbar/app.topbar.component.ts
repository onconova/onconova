import { Component, ElementRef, ViewChild } from '@angular/core';
import { MessageService } from 'primeng/api';
import { LayoutService } from "../../service/app.layout.service";
import packageInfo from '../../../../../package.json';
import { AuthService } from '../../../auth/auth.service';
import { Router } from '@angular/router';

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
        private authService: AuthService) { 

        this.profile_items = [
            {
                label: 'Logout',
                icon: 'pi pi-file',
                command: () => {
                    this.logout();
                }
            }];
    }

    toggleDarkMode() {
        const element = document.querySelector('html');
        if (element) {
            this.themeModeIcon = this.themeModeIcon == 'pi pi-moon' ? 'pi pi-sun' : 'pi pi-moon'
            element.classList.toggle('dark-mode');
        }
    }

    logout() {
        this.authService.logout()
        this.router.navigate(['login'])
        this.messageService.add({ severity: 'success', summary: 'Logout', detail: 'Succesful logout' });
    }
    
}
