import { Component, inject, OnInit,ViewEncapsulation, ChangeDetectionStrategy, ChangeDetectorRef} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { History } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { ToggleSwitchModule } from 'primeng/toggleswitch';

import { 
    FamilyHistorySchema,
    FamilyHistoryCreateSchema,
    FamilyHistoriesService,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent ,
  ReferenceMultiSelect,
  RadioChoice,
  RadioSelectComponent,
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'family-history-form',
  templateUrl: './family-history-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    ToggleSwitchModule,
    CodedConceptSelectComponent,
    RadioSelectComponent,
    ReferenceMultiSelect,
    ControlErrorComponent,
  ],
})
export class FamilyHistoryFormComponent extends AbstractFormBase implements OnInit {

    private readonly familyHistoriesService: FamilyHistoriesService = inject(FamilyHistoriesService)
    public readonly formBuilder = inject(FormBuilder)

    public readonly createService = this.familyHistoriesService.createFamilyHistory.bind(this.familyHistoriesService)
    public readonly updateService = this.familyHistoriesService.updateFamilyHistory.bind(this.familyHistoriesService)

    public readonly title: string = 'Family History'
    public readonly subtitle: string = 'Add new family history entry'
    public readonly icon = History;

    private caseId!: string;
    public initialData: FamilyHistoryCreateSchema | FamilyHistorySchema | any = {};

    public readonly contributedToDeathChoices : RadioChoice[] = [
        {name: 'Unknown', value: null},
        {name: 'Yes', value: true},
        {name: 'False', value: false},
    ]

  ngOnInit() {
    this.constructForm()
    this.form.get('hadCancer')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(hadCancer => {
        ['contributedToDeath', 'onsetAge', 'topography', 'morphology'].forEach(
            (field: string) => {
                this.form.get(field)?.setValue(null)
            }
        )
    })

  }

  constructForm(): void {
    this.form = this.formBuilder.group({
        date: [this.initialData?.date, Validators.required],
        relationship: [this.initialData?.relationship, Validators.required],
        hadCancer: [this.initialData?.hadCancer,Validators.required],
        contributedToDeath: [this.initialData?.contributedToDeath],
        onsetAge: [this.initialData?.onsetAge],
        topography: [this.initialData?.topography],
        morphology: [this.initialData?.morphology],
    });
  }
  

  constructAPIPayload(data: any): FamilyHistoryCreateSchema {    
    return {
      caseId: this.caseId,
      date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
      relationship: data.relationship,
      hadCancer: data.hadCancer,
      contributedToDeath: data.contributedToDeath,
      onsetAge: data.onsetAge,
      topography: data.topography,
      morphology: data.morphology,
    };
  }


}