import { Component, OnInit } from '@angular/core';

import { RouterOutlet } from '@angular/router';

// Messages imports 
import { MessageService } from 'primeng/api';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';


@Component({
    standalone: true,
    selector: 'pop-root',
    templateUrl: './app.component.html',
    imports:[RouterOutlet],
    providers: [MessageService],
})
export class AppComponent {
}
