import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'primeng/chart';
import { MenuModule } from 'primeng/menu';
import { TableModule } from 'primeng/table';
import { DataViewModule } from 'primeng/dataview';
import { ButtonModule } from 'primeng/button';
import { NgxJdenticonModule } from "ngx-jdenticon";
import { StyleClassModule } from 'primeng/styleclass';
import { PanelMenuModule } from 'primeng/panelmenu';
import { PatientListComponent } from './patient-list.component';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { SkeletonModule } from 'primeng/skeleton';
import { AvatarModule } from 'primeng/avatar';
import { PatientFormComponent } from './components/patient-form/patient-form.component';
import { PatientListRoutingModule } from './patient-list-routing.module';
import { DialogModule } from 'primeng/dialog';
import { ReactiveFormsModule } from '@angular/forms';
import { InputMaskModule } from 'primeng/inputmask';
import { CalendarModule } from 'primeng/calendar';
import { CodedConceptSelectModule } from '../core/components/coded-concept-select/coded-concept-select.module';
import { DateMaskDirective } from './components/patient-form/date-mask-directive'

import { ControlErrorComponent } from './components/control-error/control-error.component';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component'

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        MenuModule,
        TableModule,
        DataViewModule,
        StyleClassModule,
        PanelMenuModule,
        ButtonModule,
        NgxJdenticonModule,
        IconFieldModule,
        InputIconModule,
        InputTextModule,
        SkeletonModule,
        AvatarModule,
        PatientListRoutingModule,
        DialogModule,
        ReactiveFormsModule,
        InputMaskModule,
        CalendarModule,
        CodedConceptSelectModule,
        ControlErrorComponent,
        ModalFormComponent,
    ],
    declarations: [
        PatientListComponent,
        PatientFormComponent,
        DateMaskDirective,
    ]
})
export class CasebrowserModule { }
