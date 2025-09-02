/**
 * IdenticonComponent
 *
 * Displays a unique identicon avatar based on a provided value using Jdenticon SVG rendering.
 * The avatar is rendered inside a PrimeNG `p-avatar` component, with customizable width and height.
 *
 * - The `value` input is required and can be a string or number. It determines the identicon's appearance.
 * - The `width` and `height` inputs default to `'5rem'` if not specified.
 * - Uses `ngx-jdenticon` for SVG rendering and PrimeNG's `Avatar` for layout.
 * 
 * ```html
 * <onconova-identicon [value]="userId" width="6rem" height="6rem"></onconova-identicon>
 * ```
 *
 */
// dynamic-form-modal.component.ts
import { Component, input, ViewEncapsulation } from '@angular/core';
import { NgxJdenticonModule } from 'ngx-jdenticon';
import { Avatar } from 'primeng/avatar';


@Component({
    selector: 'onconova-identicon',
    template: `
    <p-avatar size="xlarge" [style]="{'background': 'none', 'width': width(), 'height': height(), padding: '0', 'margin': 'auto 0'}" >
        <svg class="jdenticon my-auto" [data-jdenticon-value]="value()"></svg>
    </p-avatar>
  `,
    encapsulation: ViewEncapsulation.None,
    imports: [
        Avatar,
        NgxJdenticonModule,
    ]
})
export class IdenticonComponent {
    value = input.required<string | number>();
    height = input<string>('5rem');
    width = input<string>('5rem');
}