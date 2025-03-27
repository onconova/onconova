import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { Cigarette } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    LifestyleCreate,
    LifestylesService,
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
  selector: 'lifestyle-form',
  templateUrl: './lifestyle-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    DatePickerComponent,
    Fluid,
    ButtonModule,
    ConceptSelectorComponent,
    MeasureInputComponent,
    FormControlErrorComponent,
  ],
})
export class LifestyleFormComponent extends AbstractFormBase implements OnInit {

    private readonly lifestyleService: LifestylesService = inject(LifestylesService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: LifestyleCreate) => this.lifestyleService.createLifestyle({lifestyleCreate: payload});
    public readonly updateService = (id: string, payload: LifestyleCreate) => this.lifestyleService.updateLifestyleById({lifestyleId: id, lifestyleCreate: payload});

    public readonly title: string = 'Lifestyle';
    public readonly subtitle: string = 'Add new lifestyle details';
    public readonly icon = Cigarette;

    private caseId!: string;
    public initialData: LifestyleCreate | any = {};

    public readonly smokingStatusCodeClassification = {
        neverSmoker: '266919005',
        exSmoker: '8517006', 
    }

    ngOnInit() {
        // Construct the form 
        this.constructForm()
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            smokingStatus: [this.initialData?.smokingStatus],
            smokingPackyears: [this.initialData?.smokingPackyears],
            smokingQuited: [this.initialData?.smokingQuited],
            alcoholConsumption: [this.initialData?.alcoholConsumption],
            nightSleep: [this.initialData?.nightSleep],
            recreationalDrugs: [this.initialData?.recreationalDrugs],
            exposures: [this.initialData?.exposures],
        });
    }


    constructAPIPayload(data: any): LifestyleCreate {    
        return {
            caseId: this.caseId,
            date: data.date,
            smokingStatus: data.smokingStatus,
            smokingPackyears: data.smokingPackyears,
            smokingQuited: data.smokingQuited,
            alcoholConsumption: data.alcoholConsumption,
            nightSleep: data.nightSleep,
            recreationalDrugs: data.recreationalDrugs,
            exposures: data.exposures,
        };
    }

}