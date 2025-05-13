import { Component, inject } from '@angular/core';
import { LayoutService } from "../app.layout.service";

import { InlineSVGModule } from 'ng-inline-svg-2';

@Component({
    selector: 'pop-footer',
    template:  `
        <div class="layout-footer">
            <div [inlineSVG]="logo" alt="logo" class="pop-logo mr-3"></div>
        </div>
    `,
    imports: [
        InlineSVGModule,
    ]
})
export class AppFooterComponent {
    readonly #layoutService= inject(LayoutService);
    public logo = this.#layoutService.logo
}
