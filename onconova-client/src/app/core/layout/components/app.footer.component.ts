import { Component, inject } from '@angular/core';
import { LayoutService } from "../app.layout.service";
import { InlineSVGModule } from 'ng-inline-svg-2';
import packageInfo from '../../../../../package.json';
import { environment } from 'src/environments/environment';

@Component({
    selector: 'onconova-footer',
    template:  `
        <footer class="layout-footer">
            <div [inlineSVG]="logo" alt="logo" class="onconova-logo mr-3"></div>
                <div class="footer-info">
                    <div class="footer-title">{{ organizationName }}</div>
                </div>
                <div class='footer-copyright'>Version: {{ version }} &copy; {{ year }} {{ copyrightHolder }}.</div>
        </footer>
    `,
    imports: [
        InlineSVGModule,
    ],
})
export class AppFooterComponent {
    readonly #layoutService = inject(LayoutService);
    public logo = this.#layoutService.logo;
    public readonly version = packageInfo.version;
    public readonly organizationName = environment.organizationName;

    public year = new Date().getFullYear();
    public copyrightHolder = 'Fábregas-Ibáñez, Boos, Wicki, and others';
}