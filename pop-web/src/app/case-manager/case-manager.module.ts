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
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { SkeletonModule } from 'primeng/skeleton';
import { AvatarModule } from 'primeng/avatar';
import { DialogModule } from 'primeng/dialog';
import { ToastModule } from 'primeng/toast';
import { ReactiveFormsModule } from '@angular/forms';
import { InputMaskModule } from 'primeng/inputmask';
import { CalendarModule } from 'primeng/calendar';
import { InputSwitchModule } from 'primeng/inputswitch';
import { SliderModule } from 'primeng/slider';
import { CodedConceptSelectModule } from '../core/components/coded-concept-select/coded-concept-select.module';
import { DividerModule } from 'primeng/divider';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { ChipModule } from 'primeng/chip';
import {RouterModule} from '@angular/router';
import { CaseManagerComponent } from './case-manager.component';
import { NgxJdenticonModule, JDENTICON_CONFIG } from "ngx-jdenticon";
import { PanelModule } from 'primeng/panel';
import { TimelineModule } from 'primeng/timeline';
import { BadgeModule } from 'primeng/badge';
import { CaseManagerPanelComponent } from './components/case-manager-panel/case-manager-panel.component'
import { ModalFormComponent } from '../core/components/modal-form/modal-form.component'

import { LucideAngularModule, HeartPulse, Tags, TestTubeDiagonal, Dna, Fingerprint, Microscope, Siren, DiamondPlus, Activity, Cigarette, Tablets, Slice, Radiation, Ribbon, Presentation, ShieldAlert, Image, CircleGauge} from 'lucide-angular';


@NgModule({
    imports: [
        CommonModule,
        RouterModule,
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
        DividerModule,
        AvatarGroupModule,
        InputSwitchModule,
        SliderModule,
        ToastModule,
        ChipModule,
        NgxJdenticonModule,    
        PanelModule,
        TimelineModule,
        BadgeModule,
        ModalFormComponent,
        LucideAngularModule.pick({HeartPulse, Tags, TestTubeDiagonal, Dna, Fingerprint, Microscope, Siren, DiamondPlus, Activity, Cigarette, Tablets, Slice, Radiation, Ribbon, Presentation, ShieldAlert, Image, CircleGauge}),
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
    declarations: [
        CaseManagerComponent,
        CaseManagerPanelComponent,
    ]
})
export class CaseManagerModule { }
