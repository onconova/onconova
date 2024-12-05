import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'primeng/chart';
import { MenuModule } from 'primeng/menu';
import { TableModule } from 'primeng/table';
import { DataViewModule } from 'primeng/dataview';
import { ButtonModule } from 'primeng/button';
import { StyleClassModule } from 'primeng/styleclass';
import { PanelMenuModule } from 'primeng/panelmenu';
import { CaseBrowserComponent } from './case-browser.component';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { SkeletonModule } from 'primeng/skeleton';
import { AvatarModule } from 'primeng/avatar';
import { PatientFormComponent } from '../core/forms/case-form/patient-form.component';
import { DialogModule } from 'primeng/dialog';
import { ToastModule } from 'primeng/toast';
import { ReactiveFormsModule } from '@angular/forms';
import { InputMaskModule } from 'primeng/inputmask';
import { CalendarModule } from 'primeng/calendar';
import { InputSwitchModule } from 'primeng/inputswitch';
import { SliderModule } from 'primeng/slider';
import { CodedConceptSelectModule } from '../core/components/coded-concept-select/coded-concept-select.module';
import { DateMaskDirective } from '../core/components/directives/date-mask-directive'
import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';


import { ControlErrorComponent } from '../core/components/control-error/control-error.component';
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component'
import { CaseBrowserCardComponent } from './components/case-card/case-browser-item.component';

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
        IconFieldModule,
        InputIconModule,
        InputTextModule,
        SkeletonModule,
        AvatarModule,
        DialogModule,
        ReactiveFormsModule,
        InputMaskModule,
        CalendarModule,
        CodedConceptSelectModule,
        ControlErrorComponent,
        DividerModule,
        ModalFormComponent,
        AvatarGroupModule,
        InputSwitchModule,
        SliderModule,
        ToastModule,
        ChipModule,
        CaseBrowserCardComponent
    ],
    declarations: [
        CaseBrowserComponent,
        DateMaskDirective,
        PatientFormComponent,
    ]
})
export class CaseBrowserModule { }
