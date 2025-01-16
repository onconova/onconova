import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import * as moment from 'moment'; 

import { Activity } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    VitalsCreateSchema,
    VitalsService,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent,
  RadioSelectComponent,
  MeasureInputComponent,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'vitals-form',
  templateUrl: './vitals-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    CodedConceptSelectComponent,
    MeasureInputComponent,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class VitalsFormComponent extends AbstractFormBase implements OnInit {

    private readonly vitalsService: VitalsService = inject(VitalsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = this.vitalsService.createVitals.bind(this.vitalsService);
    public readonly updateService = this.vitalsService.updateVitalsById.bind(this.vitalsService);

    public readonly title: string = 'Vitals';
    public readonly subtitle: string = 'Add new vitals';
    public readonly icon = Activity;

    private caseId!: string;
    public initialData: VitalsCreateSchema | any = {};

    ngOnInit() {
        this.constructForm()
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            height: [this.initialData?.height],
            weight: [this.initialData?.weight],
            bloodPressureDiastolic: [this.initialData?.bloodPressureDiastolic],
            bloodPressureSystolic: [this.initialData?.bloodPressureSystolic],
            temperature: [this.initialData?.temperature],
        });
    }

    constructAPIPayload(data: any): VitalsCreateSchema {    
        return {
            caseId: this.caseId,
            date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            height: data.height,
            weight: data.weight,
            bloodPressureDiastolic: data.bloodPressureDiastolic,
            bloodPressureSystolic: data.bloodPressureSystolic,
            temperature: data.temperature
        };
    }

}