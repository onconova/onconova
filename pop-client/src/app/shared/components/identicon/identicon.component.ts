// dynamic-form-modal.component.ts
import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgxJdenticonModule } from 'ngx-jdenticon';
import { Avatar } from 'primeng/avatar';


@Component({
  standalone: true,
  selector: 'pop-identicon',
  template: `
    <p-avatar size="xlarge" [style]="{'background': 'none', 'width': width, 'height': height, padding: '0', 'margin': 'auto 0'}" >
        <svg class="jdenticon my-auto" [data-jdenticon-value]="value"></svg>
    </p-avatar>
  `,
  encapsulation: ViewEncapsulation.None,
  imports: [
    Avatar,
    NgxJdenticonModule,
  ],
})
export class IdenticonComponent {
    @Input({required: true}) value!: string | number;
    @Input() height: string = '5rem';
    @Input() width: string = '5rem';
}