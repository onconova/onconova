import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';

import { 
    TerminologyService,
    PerformanceStatusCreate,
    PerformanceStatusService,
    PerformanceStatus,
} from '../../../shared/openapi'

import { 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';


type PerformanceScoreType = 'karnofsky' | 'ecog';

@Component({
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
    ]
})
export class PerformanceStatusFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<PerformanceStatus>();

    // Service injections
    readonly #performanceStatusService = inject(PerformanceStatusService);
    readonly #terminologyService = inject(TerminologyService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: PerformanceStatusCreate) => this.#performanceStatusService.createPerformanceStatus({performanceStatusCreate: payload});
    public readonly updateService = (id: string, payload: PerformanceStatusCreate) => this.#performanceStatusService.updatePerformanceStatusById({performanceStatusId: id, performanceStatusCreate: payload});

    // Define the form
    public form = this.#fb.group({
        date: this.#fb.control<string | null>(null, Validators.required),
        scoreType: this.#fb.control<PerformanceScoreType | null>(null, Validators.required),
        ecogScore: this.#fb.control<number | null>(null),
        karnofskyScore: this.#fb.control<number | null>(null),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;      
        this.form.patchValue({
            date: data.date || null,
            scoreType: data.karnofskyScore != null ? 'karnofsky' : 'ecog',
            ecogScore: data.ecogScore || null,
            karnofskyScore: data.karnofskyScore || null,
        });
    });

    // API Payload construction function
    payload = (): PerformanceStatusCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            date: data.date!,
            ecogScore: data.ecogScore,
            karnofskyScore: data.karnofskyScore,
        };
    }

    // Define human readable choices for UI elements
    public readonly scoreTypeChoices: RadioChoice[] = [
        { name: 'ECOG', value: 'ecog' },
        { name: 'Karnofsky', value: 'karnofsky' },
    ];

    // Construct human-readable list of ECOG scores with interpretations
    public ecogScores = rxResource({
        request: () => ({terminologyName: 'ECOGPerformanceStatusInterpretation'}),
        loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(map(data => {
            const ecogToInterpretation = {
                '0': 'LA9622-7', '1': 'LA9623-5', '2': 'LA9624-3',  
                '3': 'LA9625-0', '4': 'LA9626-8', '5': 'LA9627-6',        
            }
            return Array.from({length: 6}, (_, i) => ({label: `${i} | ${data.items.find(c => c.code === ecogToInterpretation[i.toString() as keyof typeof ecogToInterpretation])?.display || ''}`, value: i}));
        }))
    })

    // Construct human-readable list of Karnofsky scores with interpretations
    public karnofskyScores = rxResource({
        request: () => ({terminologyName: 'KarnofskyPerformanceStatusInterpretation'}),
        loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(map(data => {
            const karnofskyInterpretation = {
                '0': 'LA9627-6', '10': 'LA29184-1', '20': 'LA29183-3', 
                '30': 'LA29182-5', '40': 'LA29181-7', '50': 'LA29180-9', 
                '60': 'LA29179-1', '70': 'LA29178-3', '80': 'LA29177-5', 
                '90': 'LA29176-7', '100': 'LA29175-9',     
            }
            return Array.from({length: 11}, (_, i) => ({label: `${i * 10} | ${data.items.find(c => c.code === karnofskyInterpretation[(i * 10).toString() as keyof typeof karnofskyInterpretation])?.display || ''}`, value: i * 10})).reverse();
        }))
    })

    // Dynamically react to changes in the score type
    #currentScore = toSignal(this.form.get('scoreType')!.valueChanges) 
    #currentScoreChangedEffect = effect(() => {
        if (this.#currentScore() === 'ecog') {
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