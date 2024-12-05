import { CommonModule } from '@angular/common';
import { Component, Input, OnDestroy, inject } from '@angular/core';

import { PatientCase, AuthService, UserSchema } from '../../../core/modules/openapi';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';


import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";

@Component({
    selector: 'app-case-browser-item',
    templateUrl: './case-browser-item.component.html',
    imports: [
        CommonModule,
        RouterModule,
        NgxJdenticonModule,
        AvatarModule,
        AvatarGroupModule,
        DividerModule,
        ChipModule,

    ],
    providers: [
      { 
        // Custom identicon style
        provide: JDENTICON_CONFIG,
        useValue: {
            hues: [220, 230],
          lightness: {
            color: [0.21, 0.9],
            grayscale: [0.23, 0.62],
          },
          saturation: {
            color: 0.80,
            grayscale: 0.50,
          },
        },
      }
    ],
    standalone: true,
})
export class CaseBrowserCardComponent implements OnDestroy {

    private authService: AuthService = inject(AuthService);
    private subscriptions: Subscription[] = [];
    @Input() case!: PatientCase;
    public createdByUsername!: string;
    public updatedByUsernames: string[] = [];

    ngOnInit() {
        this.getCreatedByUsername()
        this.getUpdatedByUsernames()
    }

    getCreatedByUsername() {
        if (this.case.createdById) {
            this.subscriptions.push(
                this.authService.getUserById(this.case.createdById).subscribe(user => {
                    this.createdByUsername = user.username
                })
            )            
        }
    }

    getUpdatedByUsernames() {
        if (this.case.updatedByIds) {
            for (let i = 0; i<this.case.updatedByIds.length; i++) {
                this.subscriptions.push(
                    this.authService.getUserById(this.case.updatedByIds[i]).subscribe(user => {
                        this.updatedByUsernames.push(user.username)
                    })
                )
            }
        }            
    }
    
    ngOnDestroy(): void {
        this.subscriptions.forEach(subscription => subscription.unsubscribe());
    }
}

