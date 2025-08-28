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