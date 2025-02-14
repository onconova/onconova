import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { Fingerprint } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    GenomicSignatureTypes,
    TumorMutationalBurdenStatusChoices,
    HomologousRecombinationDeficiencyInterpretationChoices,
    AnyGenomicSignature,
    GenomicSignaturesService,
    TumorMutationalBurdenCreate,
    MicrosatelliteInstabilityCreate,
    TumorNeoantigenBurdenCreate,
    LossOfHeterozygosityCreate
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

export type AnyGenomicSignatureCreate = TumorMutationalBurdenCreate | MicrosatelliteInstabilityCreate |TumorNeoantigenBurdenCreate | LossOfHeterozygosityCreate;

@Component({
  standalone: true,
  selector: 'genomic-signature-form',
  templateUrl: './genomic-signature-form.component.html',
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
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class GenomicSignatureFormComponent extends AbstractFormBase implements OnInit {

    private readonly genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: AnyGenomicSignatureCreate) => this.genomicSignaturesService.createGenomicSignature({payload2: payload as any});
    public readonly updateService = (id: string, payload: AnyGenomicSignatureCreate) => this.genomicSignaturesService.updateGenomicSignatureById({genomicSignatureId: id, payload2: payload as any});

    public readonly title: string = 'Genomic Signature';
    public readonly subtitle: string = 'Add new genomic signature';
    public readonly icon = Fingerprint;

    private caseId!: string;
    public initialData: AnyGenomicSignature | any = {};

    public readonly genomicSignatureTypes = GenomicSignatureTypes;
    public readonly signatrureCategoryChoices: RadioChoice[] = [
        { name: 'Tumor mutational burden (TMB)', value: GenomicSignatureTypes.TumorMutationalBurden },
        { name: 'Microsatellite Instability (MSI)', value: GenomicSignatureTypes.MicrosatelliteInstability },
        { name: 'Loss of Heterozygosity (LOH)', value: GenomicSignatureTypes.LossOfHeterozygosity },
        { name: 'Homologous recombination deficiency (HRD)', value: GenomicSignatureTypes.HomologousRecombinationDeficiency },
        { name: 'Aneuploid Score (AS)', value: GenomicSignatureTypes.AneuploidScore },
        { name: 'Tumor neoantigen burden (TNB)', value: GenomicSignatureTypes.TumorNeoantigenBurden },
    ];

    public readonly tumorMutationalBurdernStatusChoices : RadioChoice[] = [
        { name: 'High', value: TumorMutationalBurdenStatusChoices.High},
        { name: 'Intermediate', value: TumorMutationalBurdenStatusChoices.Intermediate},
        { name: 'Low', value: TumorMutationalBurdenStatusChoices.Low},
        { name: 'Indeterminate', value: TumorMutationalBurdenStatusChoices.Indeterminate},
    ];

    public readonly homologousRecombinationDeficiencyInterpretationChoices : RadioChoice[] = [
        { name: 'Positive', value: HomologousRecombinationDeficiencyInterpretationChoices.Positive},
        { name: 'Negative', value: HomologousRecombinationDeficiencyInterpretationChoices.Negative},
        { name: 'Indeterminate', value: HomologousRecombinationDeficiencyInterpretationChoices.Indeterminate},
    ];

    ngOnInit() {
        // Construct the form 
        this.constructForm()
        this.form.get('category')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(category => {
            
            const fieldNames = [
                'tumorMutationalBurdenValue', 
                'tumorMutationalBurdenStatus', 
                'microsatelliteInstabilityValue', 
                'lossOfHeterozygosityValue',
                'homologousRecombinationDeficiencyValue',
                'homologousRecombinationDeficiencyInterpretation',
                'aneuploidScoreValue',
                'tumorNeoantigenBurdenValue',
            ]
            fieldNames.forEach(
                (field: string) => {
                    this.form.get(field)?.setValidators([])
                    this.form.get(field)?.setValue(null)
                    this.form.get(field)?.updateValueAndValidity()
                }
            )
            switch (category) {
                case GenomicSignatureTypes.TumorMutationalBurden:
                    this.form.get('tumorMutationalBurdenValue')?.setValidators([Validators.required])
                    break;
                case GenomicSignatureTypes.MicrosatelliteInstability:
                    this.form.get('microsatelliteInstabilityValue')?.setValidators([Validators.required])
                    break;
                case GenomicSignatureTypes.LossOfHeterozygosity:
                    this.form.get('lossOfHeterozygosityValue')?.setValidators([Validators.required])
                    break;      
                case GenomicSignatureTypes.HomologousRecombinationDeficiency:
                    this.form.get('homologousRecombinationDeficiencyValue')?.setValidators([])
                    break;                
                case GenomicSignatureTypes.AneuploidScore:
                    this.form.get('aneuploidScoreValue')?.setValidators([Validators.required])
                    break;                
                case GenomicSignatureTypes.TumorNeoantigenBurden:
                    this.form.get('tumorNeoantigenBurdenValue')?.setValidators([Validators.required])
                    break;       
            }
            fieldNames.forEach((field: string) => this.form.get(field)?.updateValueAndValidity())
        })
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            category: [this.initialData?.category, Validators.required],
            tumorMutationalBurdenValue: [this.initialData.category == GenomicSignatureTypes.TumorMutationalBurden ? this.initialData?.value : null],
            tumorMutationalBurdenStatus: [this.initialData.category == GenomicSignatureTypes.TumorMutationalBurden ? this.initialData?.status : null],
            microsatelliteInstabilityValue: [this.initialData.category == GenomicSignatureTypes.MicrosatelliteInstability ? this.initialData?.value : null],
            lossOfHeterozygosityValue: [this.initialData.category == GenomicSignatureTypes.LossOfHeterozygosity ? this.initialData?.value : null],
            homologousRecombinationDeficiencyValue: [this.initialData.category == GenomicSignatureTypes.HomologousRecombinationDeficiency ? this.initialData?.value : null],
            homologousRecombinationDeficiencyInterpretation: [this.initialData.category == GenomicSignatureTypes.HomologousRecombinationDeficiency ? this.initialData?.interpretation : null],
            aneuploidScoreValue: [this.initialData.category == GenomicSignatureTypes.AneuploidScore ? this.initialData?.value : null],
            tumorNeoantigenBurdenValue: [this.initialData.category == GenomicSignatureTypes.TumorNeoantigenBurden ? this.initialData?.value : null],
        });
    }


    constructAPIPayload(data: any): AnyGenomicSignatureCreate {    
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
            caseId: this.caseId,
            category: data.category,
            date: data.date,
            value: signatureValue,
            ...additionalData
        };
    }

}