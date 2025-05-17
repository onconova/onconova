import { Component } from '@angular/core';

import { RouterOutlet } from '@angular/router';
import { Toast } from 'primeng/toast';



@Component({
    selector: 'pop-root',
    template: `
        <router-outlet></router-outlet>
        <p-toast/>
    `,
    imports: [RouterOutlet, Toast],
})
export class AppComponent {
}
