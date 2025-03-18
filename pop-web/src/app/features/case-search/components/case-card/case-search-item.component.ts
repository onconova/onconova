import { CommonModule } from '@angular/common';
import { Component, Input, Output, inject, EventEmitter, ViewEncapsulation} from '@angular/core';

import { PatientCase, NeoplasticEntity, AnyStaging, StagingsService, NeoplasticEntitiesService, TherapyLinesService, TherapyLine, PatientCasesService} from 'src/app/shared/openapi';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, map, of } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';
import { Knob } from 'primeng/knob';


import { NgxJdenticonModule } from "ngx-jdenticon";

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DownloadService } from 'src/app/shared/services/download.service';

@Component({
    standalone: true,
    selector: 'pop-case-search-item',
    templateUrl: './case-search-item.component.html',
    styles: `
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
        UserBadgeComponent,
    ],
    encapsulation: ViewEncapsulation.None,
})
export class CaseBrowserCardComponent {

    // Injected services
    public authService: AuthService = inject(AuthService);
    private therapyLinesService: TherapyLinesService = inject(TherapyLinesService);
    private neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    private stagingsService: StagingsService = inject(StagingsService);
    private confirmationService: ConfirmationService = inject(ConfirmationService)
    private router: Router = inject(Router);
    private downloadService: DownloadService = inject(DownloadService)
    private caseService: PatientCasesService = inject(PatientCasesService)
    private messageService: MessageService = inject(MessageService)


    // Properties
    @Input() public case!: PatientCase;
    public createdByUsername$: Observable<string> = of('?');
    public updatedByUsernames$: Observable<string>[] = [];
    public primaryEntity$!: Observable<NeoplasticEntity>;
    public latestStaging$!: Observable<AnyStaging>;
    public latestTherapyLine$!: Observable<TherapyLine>;
    public completionProgress: number = Math.round(Math.random()*100); 
    public loadingDiagnosis: boolean = true;
    public loadingStaging: boolean = true;
    public loadingTherapyLine: boolean = true;

    @Output() delete = new EventEmitter<string>();

    actionItems = [
        {
            label: 'Export',
            disabled: !this.authService.user.canExportData,
            icon: 'pi pi-file-export',
            command: (event: any) => {
                this.messageService.add({severity: 'info', summary: 'Export in progress', detail:'Preparing data for download. Please wait.'})
                this.caseService.exportPatientCaseBundle({caseId: this.case.id}).subscribe({
                    next: response => this.downloadService.downloadAsJson(response, `POP-case-${this.case.pseudoidentifier}-bundle.json`),
                    complete: () => this.messageService.clear()
                })
            },
        },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            command: (event: any) => {
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
        this.latestTherapyLine$ = this.therapyLinesService.getTherapyLines({caseId: this.case.id}).pipe(map(data => {
            this.loadingTherapyLine = false;
            return data.items[0]
        }))
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


