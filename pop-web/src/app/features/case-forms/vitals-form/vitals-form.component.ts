import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule, formatDate } from '@angular/common';

import { Activity } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    VitalsCreate,
    VitalsService,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioSelectComponent,
  MeasureInputComponent,
} from '../../../shared/components';

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
    DatePickerComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    ConceptSelectorComponent,
    MeasureInputComponent,
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class VitalsFormComponent extends AbstractFormBase implements OnInit {

    private readonly vitalsService: VitalsService = inject(VitalsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: VitalsCreate) => this.vitalsService.createVitals({vitalsCreate: payload});
    public readonly updateService = (id: string, payload: VitalsCreate) => this.vitalsService.updateVitalsById({vitalsId: id, vitalsCreate: payload});

    public readonly title: string = 'Vitals';
    public readonly subtitle: string = 'Add new vitals';
    public readonly icon = Activity;

    private caseId!: string;
    public initialData: VitalsCreate | any = {};

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

    constructAPIPayload(data: any): VitalsCreate {    
        return {
            caseId: this.caseId,
            date: data.date,
            height: data.height,
            weight: data.weight,
            bloodPressureDiastolic: data.bloodPressureDiastolic,
            bloodPressureSystolic: data.bloodPressureSystolic,
            temperature: data.temperature
        };
    }

}