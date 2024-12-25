import { Component, OnInit } from '@angular/core';

import { RouterOutlet } from '@angular/router';

// Messages imports 
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';


@Component({
    standalone: true,
    selector: 'app-root',
    templateUrl: './app.component.html',
    imports:[RouterOutlet, ToastModule],
    providers: [MessageService],
})
export class AppComponent {
}
