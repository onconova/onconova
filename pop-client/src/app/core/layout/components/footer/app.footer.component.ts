import { Component } from '@angular/core';
import { LayoutService } from "../../app.layout.service";

import { InlineSVGModule } from 'ng-inline-svg-2';

@Component({
    standalone: true,
    selector: 'pop-footer',
    templateUrl: './app.footer.component.html',
    imports: [        
        InlineSVGModule,
    ]
})
export class AppFooterComponent {
    constructor(public layoutService: LayoutService) { }
}
