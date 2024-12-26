import { CommonModule } from '@angular/common';
import { Component, Input, inject } from '@angular/core';

import { PatientCase, AuthService, NeoplasticEntity, NeoplasticEntitiesService } from 'src/app/shared/openapi';
import { RouterModule } from '@angular/router';
import { Observable, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';


import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';

@Component({
    standalone: true,
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
        CancerIconComponent,
    ],
})
export class CaseBrowserCardComponent {

    // Injected services
    private authService: AuthService = inject(AuthService);
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    // Properties
    @Input() public case!: PatientCase;
    public createdByUsername$: Observable<string> = of('?');
    public updatedByUsernames$: Observable<string>[] = [];
    public primaryEntity$!: Observable<NeoplasticEntity>;

    ngOnInit() {
        if (this.case.createdById) {
            this.createdByUsername$ = this.authService
                    .getUserById(this.case.createdById)
                    .pipe(map(user => user.username));
        }
        if (this.case.updatedByIds) {
            this.updatedByUsernames$ = this.case.updatedByIds.map(
                id => this.authService
                        .getUserById(id)
                        .pipe(map(user => user.username))
            )
        }
        this.primaryEntity$ = this.neoplasticEntitiesService.getNeoplasticEntities(this.case.id, ['primary']).pipe(map(data => data.items[0]))
    }
}


