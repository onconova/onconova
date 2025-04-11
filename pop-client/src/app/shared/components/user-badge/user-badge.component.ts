import { Component, inject, Input, OnInit, ViewEncapsulation } from '@angular/core';

import { User } from '../../openapi';
import { GetNameAcronymPipe } from '../../pipes/name-acronym.pipe';
import { GetFullNamePipe } from '../../pipes/full-name.pipe';

import { Avatar } from 'primeng/avatar';
import { Tooltip } from 'primeng/tooltip';
import { UserBadgeService } from './user-badge.service';
import { Observable } from 'rxjs';
import { AsyncPipe } from '@angular/common';
import { Skeleton } from 'primeng/skeleton';

@Component({
    standalone: true,
    selector: 'pop-user-badge',
    styleUrl: 'user-badge.component.css',
    templateUrl: 'user-badge.component.html',
    encapsulation: ViewEncapsulation.None,
    imports: [
        AsyncPipe,
        GetNameAcronymPipe,
        GetFullNamePipe,
        Avatar,
        Skeleton,
        Tooltip,
    ]
})
export class UserBadgeComponent implements OnInit {

    private readonly userBadgeService = inject(UserBadgeService)

    @Input({required: true}) username!: string;
    public user$!: Observable<User>;

    ngOnInit() {
        this.user$ = this.userBadgeService.getUser(this.username)
    }

}