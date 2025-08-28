import { Component, effect, inject, input, linkedSignal} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';


import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    GenomicSignatureTypes,
    TumorMutationalBurdenStatusChoices,
    HomologousRecombinationDeficiencyInterpretationChoices,
    GenomicSignaturesService,
    TumorMutationalBurdenCreate,
    MicrosatelliteInstabilityCreate,
    TumorNeoantigenBurdenCreate,
    LossOfHeterozygosityCreate,
    CodedConcept,
    HomologousRecombinationDeficiencyCreate,
    AneuploidScoreCreate,
    AnyGenomicSignature,
    MicrosatelliteInstability
} from 'onconova-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { SelectButton } from "primeng/selectbutton";

export type AnyGenomicSignatureCreate = TumorMutationalBurdenCreate | 
    MicrosatelliteInstabilityCreate |
    TumorNeoantigenBurdenCreate | 
    LossOfHeterozygosityCreate | 
    HomologousRecombinationDeficiencyCreate | 
    AneuploidScoreCreate;


@Component({
    selector: 'genomic-signature-form',
    templateUrl: './genomic-signature-form.component.html',
    imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    SelectButton,
    DatePickerComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    ConceptSelectorComponent,
    FormControlErrorComponent,
    SelectButton
]
})
export class GenomicSignatureFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<AnyGenomicSignature>();

    // Service injections
    readonly #genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: AnyGenomicSignatureCreate) => this.#genomicSignaturesService.createGenomicSignature({payload2: payload as any});
    public readonly updateService = (id: string, payload: AnyGenomicSignatureCreate) => this.#genomicSignaturesService.updateGenomicSignatureById({genomicSignatureId: id, payload2: payload as any});

    // Reactive form definition
    public form = this.#fb.group({
        date: this.#fb.nonNullable.control<string>('', Validators.required),
        category: this.#fb.nonNullable.control<GenomicSignatureTypes>(GenomicSignatureTypes.TumorMutationalBurden, Validators.required),
        tumorMutationalBurdenValue: this.#fb.control<number | null>(null),
        tumorMutationalBurdenStatus: this.#fb.control<TumorMutationalBurdenStatusChoices | null>(null),
        microsatelliteInstabilityValue: this.#fb.control<CodedConcept | null>(null),
        lossOfHeterozygosityValue: this.#fb.control<number | null>(null),
        homologousRecombinationDeficiencyValue: this.#fb.control<number | null>(null),
        homologousRecombinationDeficiencyInterpretation: this.#fb.control<HomologousRecombinationDeficiencyInterpretationChoices | null>(null),
        aneuploidScoreValue: this.#fb.control<number | null>(null),
        tumorNeoantigenBurdenValue: this.#fb.control<number | null>(null),
      });
    
    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;        
        this.form.patchValue({
            date: data.date ?? '',
            category: data.category ?? GenomicSignatureTypes.TumorMutationalBurden,
            tumorMutationalBurdenValue: data.category === GenomicSignatureTypes.TumorMutationalBurden ? data.value ?? null : null,
            tumorMutationalBurdenStatus: data.category === GenomicSignatureTypes.TumorMutationalBurden ? data.status ?? null : null,
            microsatelliteInstabilityValue: data.category === GenomicSignatureTypes.MicrosatelliteInstability ? (data as unknown as MicrosatelliteInstability)?.value ?? null : null,
            lossOfHeterozygosityValue: data.category === GenomicSignatureTypes.LossOfHeterozygosity ? data.value ?? null : null,
            homologousRecombinationDeficiencyValue: data.category === GenomicSignatureTypes.HomologousRecombinationDeficiency ? data.value ?? null : null,
            homologousRecombinationDeficiencyInterpretation: data.category === GenomicSignatureTypes.HomologousRecombinationDeficiency ? data.interpretation ?? null : null,
            aneuploidScoreValue: data.category === GenomicSignatureTypes.AneuploidScore ? data.value ?? null : null,
            tumorNeoantigenBurdenValue: data.category === GenomicSignatureTypes.TumorNeoantigenBurden ? data.value ?? null : null,
        });
    });
    // Data for the form UI elements
    public readonly genomicSignatureTypes = GenomicSignatureTypes;
    public readonly signatrureCategoryChoices: RadioChoice[] = [
        { name: 'Tumor mutational burden (TMB)', value: GenomicSignatureTypes.TumorMutationalBurden },
        { name: 'Microsatellite Instability (MSI)', value: GenomicSignatureTypes.MicrosatelliteInstability },
        { name: 'Loss of Heterozygosity (LOH)', value: GenomicSignatureTypes.LossOfHeterozygosity },
        { name: 'Homologous recombination deficiency (HRD)', value: GenomicSignatureTypes.HomologousRecombinationDeficiency },
        { name: 'Aneuploid Score (AS)', value: GenomicSignatureTypes.AneuploidScore },
        { name: 'Tumor neoantigen burden (TNB)', value: GenomicSignatureTypes.TumorNeoantigenBurden },
    ];
    public readonly tumorMutationalBurdernStatusChoices = [
        { label: 'High', value: TumorMutationalBurdenStatusChoices.High},
        { label: 'Intermediate', value: TumorMutationalBurdenStatusChoices.Intermediate},
        { label: 'Low', value: TumorMutationalBurdenStatusChoices.Low},
        { label: 'Indeterminate', value: TumorMutationalBurdenStatusChoices.Indeterminate},
    ];
    public readonly homologousRecombinationDeficiencyInterpretationChoices = [
        { label: 'Positive', value: HomologousRecombinationDeficiencyInterpretationChoices.Positive},
        { label: 'Negative', value: HomologousRecombinationDeficiencyInterpretationChoices.Negative},
        { label: 'Indeterminate', value: HomologousRecombinationDeficiencyInterpretationChoices.Indeterminate},
    ];

    // Function to prepare API payload from form data
    readonly payload = (): AnyGenomicSignatureCreate => {    
        let data = this.form.value;
        let signatureValue: any
        let additionalData: object = {}
        switch (data.category) {
            case GenomicSignatureTypes.TumorMutationalBurden:
                signatureValue = data.tumorMutationalBurdenValue;
                additionalData = {status: data.tumorMutationalBurdenStatus};
                break;
            case GenomicSignatureTypes.MicrosatelliteInstability:
                signatureValue = data.microsatelliteInstabilityValue;
                break;
            case GenomicSignatureTypes.LossOfHeterozygosity:
                signatureValue = data.lossOfHeterozygosityValue;
                break;      
            case GenomicSignatureTypes.HomologousRecombinationDeficiency:
                signatureValue = data.homologousRecombinationDeficiencyValue;
                additionalData = {interpretation: data.homologousRecombinationDeficiencyInterpretation};
                break;                
            case GenomicSignatureTypes.AneuploidScore:
                signatureValue = data.aneuploidScoreValue;
                break;                
            case GenomicSignatureTypes.TumorNeoantigenBurden:
                signatureValue = data.tumorNeoantigenBurdenValue;
                break;                          
        } 
        return {
            caseId: this.caseId(),
            category: data.category,
            date: data.date as string,
            value: signatureValue,
            ...additionalData
        };
    }


    #selectedCategory = toSignal(this.form.get('category')!.valueChanges)
    #onCategoryChange = effect(() => {
        if (this.#selectedCategory()) {
            this.handleCategoryChange(this.#selectedCategory() as string)
        }
    })
    
    handleCategoryChange(category: string) {             
        // List of all fields to reset
        const fieldsToReset = [
            'tumorMutationalBurdenValue',
            'tumorMutationalBurdenStatus',
            'microsatelliteInstabilityValue',
            'lossOfHeterozygosityValue',
            'homologousRecombinationDeficiencyValue',
            'homologousRecombinationDeficiencyInterpretation',
            'aneuploidScoreValue',
            'tumorNeoantigenBurdenValue',
        ];
        // Map of which field gets required validator depending on category
        const categoryValidators: Record<string, string> = {
            [GenomicSignatureTypes.TumorMutationalBurden]: 'tumorMutationalBurdenValue',
            [GenomicSignatureTypes.MicrosatelliteInstability]: 'microsatelliteInstabilityValue',
            [GenomicSignatureTypes.LossOfHeterozygosity]: 'lossOfHeterozygosityValue',
            [GenomicSignatureTypes.AneuploidScore]: 'aneuploidScoreValue',
            [GenomicSignatureTypes.TumorNeoantigenBurden]: 'tumorNeoantigenBurdenValue',
            [GenomicSignatureTypes.HomologousRecombinationDeficiency]: 'homologousRecombinationDeficiencyValue',
        };
        // Reset fields: clear value and validators
        fieldsToReset.forEach(field => {
            const control = this.form.get(field);
            if (control) {
            control.clearValidators();
            }
        });

        // Apply new validator if category has a mapped field
        const requiredField = categoryValidators[category];
        if (requiredField) {
            this.form.get(requiredField)?.setValidators([Validators.required]);
        }

        // Update validity in a single pass
        fieldsToReset.forEach(field => this.form.get(field)?.updateValueAndValidity());
    }

}