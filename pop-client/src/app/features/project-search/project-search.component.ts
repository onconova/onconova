import { Component, computed, inject, input, OnInit, Signal, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { UsersService, User, UserCreate, ProjectsService, Project, ProjectStatusChoices, GetAllProjectHistoryEventsRequestParams, GetProjectsRequestParams } from 'pop-api-client';
import { catchError, first, map, of, tap } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ModalFormHeaderComponent } from 'src/app/features/forms/modal-form-header.component';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { GraduationCap, User as UserIcon } from 'lucide-angular';
import { rxResource } from '@angular/core/rxjs-interop';
import { MessageService } from 'primeng/api';
import { UserFormComponent } from 'src/app/core/admin/forms/user-form/user-form.component';
import { Skeleton } from 'primeng/skeleton';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { TagModule } from 'primeng/tag';
import { UserBadgeComponent } from 'src/app/shared/components/user-badge/user-badge.component';
import { Toolbar } from 'primeng/toolbar';
import { IconField, IconFieldModule } from 'primeng/iconfield';
import { NgxCountAnimationDirective } from 'ngx-count-animation';
import { OverlayBadgeModule } from 'primeng/overlaybadge';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { DataViewModule } from 'primeng/dataview';
import { Divider } from 'primeng/divider';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { ProjectSearchItemComponent } from './components/project-search-item.component';
import { ProjectFormComponent } from '../forms/projects-form/projects-form.component';
import { PopoverFilterButtonComponent } from 'src/app/shared/components/popover-filter-button/popover-filter-button.component';
import { SelectButton } from 'primeng/selectbutton';
import { driver } from 'driver.js';
import TourDriverConfig from './project-search.tour';
import { Select } from 'primeng/select';

@Component({
    selector: 'pop-project-search',
    templateUrl: './project-search.component.html',
    imports: [
        CommonModule,
        ProjectSearchItemComponent,
        PopoverFilterButtonComponent,
        NgxCountAnimationDirective,
        FormsModule,
        TableModule,
        ButtonModule,
        IconFieldModule,
        SelectButton,
        OverlayBadgeModule,
        InputIconModule,
        InputTextModule,
        ButtonModule,
        DataViewModule,
        Skeleton,
        Select,
        CardModule,
        TagModule,
        Toolbar,
        IconField,
    ],
    animations: [
        trigger('fadeAnimation', [
            state('void', style({ opacity: 0 })), // Initial state (not visible)
            transition(':enter', [animate('500ms ease-in')]), // Fade-in effect
            transition(':leave', [animate('200ms ease-out')]) // Fade-out effect
        ])
    ]
})
export class ProjectSearchComponent {

    // Reactive input properties
    public readonly member = input<string | null>();
    

    
    // Injected services
    readonly #projectsService = inject(ProjectsService);
    readonly #authService = inject(AuthService)
    readonly #messageService = inject(MessageService); 
    readonly #dialogservice = inject(DialogService);

    // Resources
    public projects = rxResource({
        request: () => ({
            titleContains: this.searchQuery() || undefined, 
            membersUsername: this.member() || undefined,  
            status: this.selectedStatus()?.value || undefined,
            limit: this.pagination().limit, 
            offset: this.pagination().offset,
            ordering: this.ordering() || '-createdAt',
        } as GetProjectsRequestParams),
        loader: ({request}) => this.#projectsService.getProjects(request).pipe(
            tap(page => this.totalProjects.set(page.count)),
            map(page => page.items),
            catchError((error: any) => {
                this.#messageService.add({ severity: 'error', summary: 'Error loading projects', detail: error?.error?.detail });
                return of([] as Project[]) 
            })
        )
    })

    // Computed properties
    public searchQuery = signal<string>('');
    public selectedStatus = signal<any>('');
    public readonly currentUser = computed(() => this.#authService.user());
    public readonly isPersonalPage = computed(() => this.member() !== undefined);
    
    // Pagination and search settings
    public readonly pageSizeChoices: number[] = [12, 24, 36, 48];
    public pagination = signal({limit: this.pageSizeChoices[0], offset: 0});
    public layout: Signal<'grid' | 'list'> = signal('grid');
    public totalProjects= signal(0);
    public currentOffset: number = 0;

    protected projectStatusChoices: any[] = [
        {label: 'Planned', value: ProjectStatusChoices.Planned},
        {label: 'Ongoing', value: ProjectStatusChoices.Ongoing},
        {label: 'Completed', value: ProjectStatusChoices.Completed},
        {label: 'Aborted', value: ProjectStatusChoices.Aborted},
    ];
    protected orderingFields = [
        {label: 'Creation date', value: 'createdAt'},
        {label: 'Last Updated', value: 'updatedAt'},
        {label: 'Title', value: 'title'},
        {label: 'Status', value: 'status'},
    ]
    protected orederingDirections = [
        {label: 'Descending', value: '-'},
        {label: 'Ascending', value: ''},
    ]
    protected orderingField = signal<string>(this.orderingFields[0].value)
    protected orderingDirection = signal<string>(this.orederingDirections[0].value)
    protected ordering = computed(() => this.orderingDirection() + this.orderingField()) 
    protected tour = TourDriverConfig;

    // Modal form config
    #modalFormConfig = computed( () => ({
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
    }))
    #modalFormRef: DynamicDialogRef | undefined;


    public openProjectForm(initialData?: Project) {    
        this.#modalFormRef = this.#dialogservice.open(ProjectFormComponent, {
            inputValues: {
                initialData: initialData,
                resourceId: initialData ? initialData.id : undefined,
            },
            data: {
                title: 'Project',
                subtitle: "Register a new project",
                icon: GraduationCap,
            },
            ...this.#modalFormConfig()
        })
        this.reloadDataIfClosedAndSaved(this.#modalFormRef)
    }

    reloadDataIfClosedAndSaved(modalFormRef: DynamicDialogRef) {
        modalFormRef.onClose.subscribe((data: any) => {
            if (data?.saved) {
                this.projects.reload()
            }
        })    
    }
    
    showSelectedChoiceFilter(choice: {label: string, value: any}): string {
        return choice.label
    }

    startTour() {
        driver(this.tour).drive()    
    }
}


