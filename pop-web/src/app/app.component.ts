import { Component, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    providers: [MessageService],
})
export class AppComponent implements OnInit {


    ngOnInit() {
    }
}
