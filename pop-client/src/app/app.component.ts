import { Component, OnInit } from '@angular/core';

import { RouterOutlet } from '@angular/router';



@Component({
    selector: 'pop-root',
    template: `<router-outlet></router-outlet>`,
    imports: [RouterOutlet],
})
export class AppComponent {
}
