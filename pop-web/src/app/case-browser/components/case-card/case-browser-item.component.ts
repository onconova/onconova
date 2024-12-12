import { CommonModule } from '@angular/common';
import { Component, Input, inject } from '@angular/core';

import { PatientCase, AuthService, NeoplasticEntity, NeoplasticEntitiesService } from '../../../core/modules/openapi';
import { RouterModule } from '@angular/router';
import { Observable, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';


import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";

import { CancerIconComponent } from 'src/app/core/components/cancer-icon/cancer-icon.component';

/**
 * Represents a single case browser item.
 *
 * This component is used to display information about a specific patient case in a case browser or list.
 * It takes a `PatientCase` object as input and fetches the usernames of the users who created and updated the case.
 *
 * @example
 * <app-case-browser-item [case]="patientCase"></app-case-browser-item>
 *
 * @property {PatientCase} case - The patient case object.
 * @property {Observable<string>} createdByUsername$ - An observable that emits the username of the user who created the case.
 * @property {Observable<string>[]} updatedByUsernames$ - An array of observables that emit the usernames of the users who updated the case.
 *
 * @dependencies
 * - AuthService: Used to fetch the usernames of the users who created and updated the case.
 */
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
    providers: [
      { 
        // Custom identicon style
        provide: JDENTICON_CONFIG,
        useValue: {
            hues: [0, 0],
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


