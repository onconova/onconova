import { CommonModule } from '@angular/common';
import { Component, Output, inject, EventEmitter, input, Resource, computed} from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';

import { PatientCase, NeoplasticEntity, AnyStaging, StagingsService, NeoplasticEntitiesService, TherapyLinesService, TherapyLine, PatientCasesService, InteroperabilityService} from 'pop-api-client';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { first, map } from 'rxjs';

import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import { AvatarModule } from 'primeng/avatar';
import { SplitButtonModule } from 'primeng/splitbutton';
import { ConfirmationService, MessageService, MenuItem } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { SkeletonModule } from 'primeng/skeleton';
import { Knob } from 'primeng/knob';

import { CancerIconComponent } from 'src/app/shared/components/cancer-icon/cancer-icon.component';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { DownloadService } from 'src/app/shared/services/download.service';
import { IdenticonComponent } from "../../../../../shared/components/identicon/identicon.component";
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { PatientFormComponent } from 'src/app/features/forms';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';
import { UserPlus } from 'lucide-angular';

@Component({
    selector: 'pop-case-search-item',
    templateUrl: './case-search-item.component.html',
    providers: [
        ConfirmationService,
    ],
    imports: [
        CommonModule,
        FormsModule,
        RouterModule,
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
        IdenticonComponent
    ]
})
export class CaseSearchItemCardComponent {

    @Output() public onDelete = new EventEmitter();

    // Injected services
    readonly #authService = inject(AuthService);
    readonly #caseService = inject(PatientCasesService);
    readonly #therapyLinesService = inject(TherapyLinesService);
    readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #stagingsService = inject(StagingsService);
    readonly #confirmationService = inject(ConfirmationService);
    readonly #dialogservice = inject(DialogService)
    readonly #router = inject(Router);
    readonly #downloadService = inject(DownloadService);
    readonly #messageService = inject(MessageService);
    readonly #interoperabilityService = inject(InteroperabilityService);
    #modalFormRef: DynamicDialogRef | undefined;

    // Properties
    public readonly case = input.required<PatientCase>();
    public readonly currentUser = computed(() => this.#authService.user());
    public caseData = rxResource({
        request: () => ({caseId: this.case().id, anonymized: this.currentUser().canManageCases ? false : true}),
        loader: ({request}) => this.#caseService.getPatientCaseById(request),
    });
    public primaryEntity: Resource<NeoplasticEntity | undefined> = rxResource({
        request: () => ({caseId: this.case().id, relationship: 'primary', limit: 1}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(data => data.items[0])),
    });
    public latestStaging: Resource<AnyStaging | undefined> = rxResource({
        request: () => ({caseId: this.case().id, limit: 1}),
        loader: ({request}) => this.#stagingsService.getStagings(request).pipe(map(data => data.items[0])),
    });
    public latestTherapyLine: Resource<TherapyLine | undefined> = rxResource({
        request: () => ({caseId: this.case().id, limit: 1}),
        loader: ({request}) => this.#therapyLinesService.getTherapyLines(request).pipe(map(data => data.items[0])),
    });
    public readonly actionItems: MenuItem[] = [
        {
            label: 'Export',
            disabled: !this.currentUser().canExportData,
            icon: 'pi pi-file-export',
            command: () => this.exportCaseBundle,
        },
        {
            label: 'Delete',
            icon: 'pi pi-trash',
            styleClass: 'delete-action',
            disabled: !this.currentUser().canManageCases,
            command: (event: any) => this.confirmDelete(event),
        },
        {
            label: 'Update',
            icon: 'pi pi-pencil',
            disabled: !this.currentUser().canManageCases,
            command: (event: any) => this.openUpdateCaseForm(),
        },
    ];

    openCaseManagement() {
        this.#router.navigate(['cases/management',this.case().pseudoidentifier])
    }

    exportCaseBundle() {
        const filename = `POP-case-${this.case().pseudoidentifier}-bundle.json`;
        this.#messageService.add({severity: 'info', summary: 'Export in progress', detail:'Preparing data for download. Please wait.'})
        this.#interoperabilityService.exportPatientCaseBundle({caseId: this.case().id}).pipe(first()).subscribe({
            next: response => this.#downloadService.downloadAsJson(response, filename),
            complete: () => this.#messageService.add({ severity: 'success', summary: 'Successfully exported', detail: filename }),
            error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error exporting case', detail: error?.error?.detail })
        })
    }

    confirmDelete(event: any) {
        this.#confirmationService.confirm({
            target: event.target as EventTarget,
            header: 'Danger Zone',
            message: `
                Are you sure you want to delete this case? 
                <div class="mt-2 font-bold text-secondary">
                    <small>${this.case().pseudoidentifier}</small><br>
                    <small>${this.case().age} years, ${this.case().gender.display}</small>
                </div>
            `,
            icon: 'pi pi-exclamation-triangle',
            rejectButtonProps: {label: 'Cancel', severity: 'secondary', outlined: true},
            acceptButtonProps: {label: 'Delete', severity: 'danger'},
            accept: () => {
                this.#caseService.deletePatientCaseById({caseId: this.case().id}).pipe(first()).subscribe({
                    complete: () => {
                        this.onDelete.emit();
                        this.#messageService.add({ severity: 'success', summary: 'Successfully deleted', detail: this.case().pseudoidentifier })
                    },
                    error: (error: any) => this.#messageService.add({ severity: 'error', summary: 'Error deleting case', detail: error?.error?.detail })
                })
            }
        });
    }


    openUpdateCaseForm() {    
        this.#modalFormRef = this.#dialogservice.open(PatientFormComponent, {
            inputValues: {
                    resourceId: this.case().id,
                    initialData: this.caseData.value(),
            },
            data: {
                title: 'Patient case registration',
                subtitle: 'Add a new patient case',
                icon: UserPlus,
            },
            templates: {
                header: ModalFormHeaderComponent,
            },   
            modal: true,
            closable: true,
            width: '45vw',
            styleClass: 'pop-modal-form',
            breakpoints: {
                '1700px': '50vw',
                '960px': '75vw',
                '640px': '90vw'
            },
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
    modalFormRef.onClose.subscribe((data: any) => {
        if (data?.saved) {
            this.onDelete.emit();
        }
        })    
    }

}


