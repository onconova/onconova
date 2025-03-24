import { Component, Input, ViewEncapsulation } from '@angular/core';

import { User } from '../../openapi';
import { GetNameAcronymPipe } from '../../pipes/name-acronym.pipe';
import { GetFullNamePipe } from '../../pipes/full-name.pipe';

import { Avatar } from 'primeng/avatar';
import { Tooltip } from 'primeng/tooltip';

@Component({
    standalone: true,
    selector: 'pop-user-badge',
    styleUrl: 'user-badge.component.css',
    templateUrl: 'user-badge.component.html',
    encapsulation: ViewEncapsulation.None,
    imports: [
        GetNameAcronymPipe,
        GetFullNamePipe,
        Avatar,
        Tooltip,
    ]
})
export class UserBadgeComponent {

    @Input({required: true}) user!: User

}