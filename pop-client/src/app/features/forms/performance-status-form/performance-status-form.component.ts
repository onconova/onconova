import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { CircleGauge } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    CodedConcept,
    TerminologyService,
    PerformanceStatusCreate,
    PerformanceStatusService,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
  standalone: true,
  selector: 'performance-status-form',
  templateUrl: './performance-status-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    DatePickerComponent,
    Fluid,
    ButtonModule,
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class PerformanceStatusFormComponent extends AbstractFormBase implements OnInit {

    private readonly performanceStatusService: PerformanceStatusService = inject(PerformanceStatusService);
    private readonly terminologyService: TerminologyService = inject(TerminologyService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: PerformanceStatusCreate) => this.performanceStatusService.createPerformanceStatus({performanceStatusCreate: payload});
    public readonly updateService = (id: string, payload: PerformanceStatusCreate) => this.performanceStatusService.updatePerformanceStatusById({performanceStatusId: id, performanceStatusCreate: payload});

    public readonly title: string = 'Performance Status';
    public readonly subtitle: string = 'Add new performance status';
    public readonly icon = CircleGauge;

    private caseId!: string;
    public initialData: PerformanceStatusCreate | any = {};

    public ecogScores = [
        {label: '0', value: 0},
        {label: '1', value: 1},
        {label: '2', value: 2},
        {label: '3', value: 3},
        {label: '4', value: 4},
        {label: '5', value: 5},
    ];
    public karnofskyScores = [
        {label: '0', value: 0},
        {label: '10', value: 10},
        {label: '20', value: 20},
        {label: '30', value: 30},
        {label: '40', value: 40},
        {label: '50', value: 50},
        {label: '60', value: 60},
        {label: '70', value: 70},
        {label: '80', value: 80},
        {label: '90', value: 90},
        {label: '100', value: 100},
    ].reverse();

    public readonly scoreTypeChoices: RadioChoice[] = [
        { name: 'ECOG', value: 'ecog' },
        { name: 'Karnofsky', value: 'karnofsky' },
    ];

    ngOnInit() {
        // Add the interpretration
        this.terminologyService.getTerminologyConcepts({terminologyName: 'ECOGPerformanceStatusInterpretation'}).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: data => {
                data.items.forEach(
                    (concept: CodedConcept, idx: number) => {
                        this.ecogScores[idx].label = `${this.ecogScores[idx].label} | ${concept.display || ''}`;
                    }
                )
            }
        });
        this.terminologyService.getTerminologyConcepts({terminologyName: 'KarnofskyPerformanceStatusInterpretation'}).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: data => {
                data.items.forEach(
                    (concept: CodedConcept, idx: number) => {
                        this.karnofskyScores[idx].label = `${this.karnofskyScores[idx].label} | ${concept.display || ''}`;
                    }
                )
            }
        });

        // Construct the form 
        this.constructForm()
        this.form.get('scoreType')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(scoreType => {
            if (scoreType === 'ecog') {
                this.form.get('ecogScore')?.setValidators([Validators.required])
                this.form.get('karnofskyScore')?.setValidators([])
                this.form.get('karnofskyScore')?.setValue(null)
            } else {
                this.form.get('ecogScore')?.setValidators([])
                this.form.get('karnofskyScore')?.setValidators([Validators.required])
                this.form.get('ecogScore')?.setValue(null)
            }
            this.form.get('ecogScore')?.updateValueAndValidity()
            this.form.get('karnofskyScore')?.updateValueAndValidity()
        })
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            scoreType: [this.initialData?.karnofskyScore != null ? 'karnofsky' : 'ecog', Validators.required],
            ecogScore: [this.initialData?.ecogScore],
            karnofskyScore: [this.initialData?.karnofskyScore],
        });
    }


    constructAPIPayload(data: any): PerformanceStatusCreate {    
        return {
            caseId: this.caseId,
            date: data.date,
            ecogScore: data.ecogScore,
            karnofskyScore: data.karnofskyScore,
        };
    }

}