import { CommonModule } from '@angular/common';
import { Component, Input, Output, inject, EventEmitter, ViewEncapsulation} from '@angular/core';

import { PatientCase, AuthService, NeoplasticEntity, AnyStaging, StagingsService, NeoplasticEntitiesService } from 'src/app/shared/openapi';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';
import { Knob } from 'primeng/knob';


import { NgxJdenticonModule } from "ngx-jdenticon";

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';

@Component({
    standalone: true,
    selector: 'pop-case-search-item',
    templateUrl: './case-search-item.component.html',
    styles: `
        .manager-avatar.p-avatar {
            color: var(--p-primary-500) !important;
            background: color-mix(in srgb, var(--p-primary-500), transparent 80%)  !important;
        }
        text.p-knob-text::after {
            content: '%' !important;
        }
    `,
    providers: [
        ConfirmationService,
    ],
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
        NgxJdenticonModule,
        AvatarModule,
        AvatarGroupModule,
        DividerModule,
        SplitButtonModule,
        ConfirmDialogModule,
        ChipModule,
        Knob,
        SkeletonModule,
        CancerIconComponent,
    ],
    encapsulation: ViewEncapsulation.None,
})
export class CaseBrowserCardComponent {

    // Injected services
    private authService: AuthService = inject(AuthService);
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    private stagingsService: StagingsService = inject(StagingsService);
    private confirmationService: ConfirmationService = inject(ConfirmationService)
    private router: Router = inject(Router);

    // Properties
    @Input() public case!: PatientCase;
    public createdByUsername$: Observable<string> = of('?');
    public updatedByUsernames$: Observable<string>[] = [];
    public primaryEntity$!: Observable<NeoplasticEntity>;
    public latestStaging$!: Observable<AnyStaging>;
    public latestTherapyLine$!: Observable<string>;
    public completionProgress: number = Math.round(Math.random()*100); 
    public loadingDiagnosis: boolean = true;
    public loadingStaging: boolean = true;

    @Output() delete = new EventEmitter<string>();

    actionItems = [
        {
            label: 'Export',
            icon: 'pi pi-file-export',
            command: (event: any) => {
                console.log('export', this.case.id)
            },
        },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            command: (event: any) => {
                console.log('delete', this.case.id)
                this.confirmDelete(event);
            },
        },
    ];

    ngOnInit() {
        this.primaryEntity$ = this.neoplasticEntitiesService.getNeoplasticEntities({caseId: this.case.id, relationship:'primary'}).pipe(map(data => {
            this.loadingDiagnosis = false;
            return data.items[0]
        }))
        this.latestStaging$ = this.stagingsService.getStagings({caseId: this.case.id}).pipe(map(data => {
            this.loadingStaging = false;
            return data.items[0]
        }))
        this.latestTherapyLine$ = of(`${this.getRandomInt(0,10)>2 ? 'P' : 'C'}LoT${this.getRandomInt(1,6)}`)
    }

    openCaseManagement() {
        this.router.navigate(['cases/management',this.case.pseudoidentifier])
    }

    confirmDelete(event: any) {
        this.confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Danger Zone',
            message: `Are you sure you want to delete this case? 
            <div class="mt-2 font-bold text-secondary">
            <small>${this.case.pseudoidentifier}</small><br>
            <small>${this.case.age} years, ${this.case.gender.display}</small>
            </div>
            `,
            icon: 'pi pi-exclamation-triangle',
            rejectButtonProps: {
                label: 'Cancel',
                severity: 'secondary',
                outlined: true
            },
            acceptButtonProps: {
                label: 'Delete',
                severity: 'danger',
            },
            accept: () => {
                this.delete.emit(this.case.id);
            }
        });
    }


    getRandomInt(min: number, max: number): number {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

}


