import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { SelectButton } from 'primeng/selectbutton';
import { InputTextModule } from 'primeng/inputtext';

import openApiSchema from "../../../../../openapi.json";
import { 
    GenomicVariantCreate,
    GenomicVariantsService,
    GenomicVariantClinicalRelevanceChoices,
    GenomicVariantConfidenceChoices,
    GenomicVariantAssessmentChoices,
    GenomicVariant,
    CodedConcept,
} from 'pop-api-client'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { Fieldset } from 'primeng/fieldset';
import { Divider } from 'primeng/divider';

@Component({
    selector: 'genomic-variant-form',
    templateUrl: './genomic-variant-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        DatePickerComponent,
        SelectButton,
        Fluid,
        Fieldset,
        Divider,
        InputNumber,
        InputTextModule,
        ButtonModule,
        ConceptSelectorComponent,
        FormControlErrorComponent,
    ]
})
export class GenomicVariantFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<GenomicVariant>();

    // Service injections using Angular's `inject()` API
    readonly #genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: GenomicVariantCreate) => this.#genomicVariantsService.createGenomicVariant({genomicVariantCreate: payload});
    public readonly updateService = (id: string, payload: GenomicVariantCreate) => this.#genomicVariantsService.updateGenomicVariant({genomicVariantId: id, genomicVariantCreate: payload});
   
    // Define the form
    public form = this.#fb.group({
      date: this.#fb.control<string | null>(null, Validators.required),
      assessmentDate: this.#fb.control<string | null>(null),
      genePanel: this.#fb.control<string | null>(null),
      assessment: this.#fb.control<GenomicVariantAssessmentChoices | null>(null),
      confidence: this.#fb.control<GenomicVariantConfidenceChoices | null>(null),
      analysisMethod: this.#fb.control<CodedConcept | null>(null, Validators.required),
      clinicalRelevance: this.#fb.control<GenomicVariantClinicalRelevanceChoices | null>(null),
      genes: this.#fb.control<CodedConcept[] | null>(null, Validators.required),
      dnaHgvs: this.#fb.control<string | null>(null, [Validators.required, Validators.pattern(this.extractRegexPattern('dnaHgvs'))]),
      rnaHgvs: this.#fb.control<string | null>(null, Validators.pattern(this.extractRegexPattern('rnaHgvs'))),
      proteinHgvs: this.#fb.control<string | null>(null, Validators.pattern(this.extractRegexPattern('proteinHgvs'))),
      copyNumber: this.#fb.control<number | null>(null),
      molecularConsequence: this.#fb.control<CodedConcept | null>(null),
      alleleFrequency: this.#fb.control<number | null>(null),
      alleleDepth: this.#fb.control<number | null>(null),
      zygosity: this.#fb.control<CodedConcept | null>(null),
      inheritance: this.#fb.control<CodedConcept | null>(null),
      clinvar: this.#fb.control<string | null>(null),
    });
    
    // API Payload construction function
    payload = (): GenomicVariantCreate => {   
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            date: data.date!,
            assessmentDate: data.assessmentDate!,
            genes: data.genes!,
            genePanel: data.genePanel!,            
            assessment: data.assessment,            
            confidence: data.confidence,            
            analysisMethod: data.analysisMethod!,   
            clinicalRelevance: data.clinicalRelevance,   
            dnaHgvs: data.dnaHgvs,   
            rnaHgvs: data.rnaHgvs,   
            proteinHgvs: data.proteinHgvs,   
            molecularConsequence: data.molecularConsequence,   
            clinvar: data.clinvar,    
            alleleFrequency: data.alleleFrequency,   
            copyNumber: data.copyNumber,   
            alleleDepth: data.alleleDepth,   
            zygosity: data.zygosity,   
            inheritance: data.inheritance        
        };
    }
    
    readonly #onInitialDataChangeEffect = effect((): void => {
      const data = this.initialData();
      if (!data) return;
    
      this.form.patchValue({
        date: data.date ?? null,
        assessmentDate: data.assessmentDate ?? null,
        genePanel: data.genePanel ?? null,
        assessment: data.assessment ?? null,
        confidence: data.confidence ?? null,
        analysisMethod: data.analysisMethod ?? null,
        clinicalRelevance: data.clinicalRelevance ?? null,
        genes: data.genes ?? null,
        dnaHgvs: data.dnaHgvs ?? null,
        rnaHgvs: data.rnaHgvs ?? null,
        proteinHgvs: data.proteinHgvs ?? null,
        copyNumber: data.copyNumber ?? null,
        molecularConsequence: data.molecularConsequence ?? null,
        alleleFrequency: data.alleleFrequency ?? null,
        alleleDepth: data.alleleDepth ?? null,
        zygosity: data.zygosity ?? null,
        inheritance: data.inheritance ?? null,
        clinvar: data.clinvar ?? null,
      });
    });

    public confidenceChoices: RadioChoice[] = [
        {name: 'Low', value: GenomicVariantConfidenceChoices.Low},
        {name: 'High', value: GenomicVariantConfidenceChoices.High},
        {name: 'Indeterminate', value: GenomicVariantConfidenceChoices.Indeterminate},
    ]

    public assessmentChoices: RadioChoice[] = [
        {name: 'Present', value: GenomicVariantAssessmentChoices.Present},
        {name: 'Absent', value: GenomicVariantAssessmentChoices.Absent},
        {name: 'No Call', value: GenomicVariantAssessmentChoices.NoCall},
        {name: 'Indeterminate', value: GenomicVariantAssessmentChoices.Indeterminate},
    ]

    public clinicalRelevanceChoices: RadioChoice[] = [
        {name: 'Pathogenic', value: GenomicVariantClinicalRelevanceChoices.Pathogenic},
        {name: 'Likely pathogenic', value: GenomicVariantClinicalRelevanceChoices.LikelyPathogenic},
        {name: 'Benign', value: GenomicVariantClinicalRelevanceChoices.Benign},
        {name: 'Likely benign', value: GenomicVariantClinicalRelevanceChoices.LikelyBenign},
        {name: 'Ambiguous', value: GenomicVariantClinicalRelevanceChoices.Ambiguous},
        {name: 'Uncertain significance', value: GenomicVariantClinicalRelevanceChoices.UncertainSignificance},
    ]


    private extractRegexPattern(propertyName: string): string {
        const schema = openApiSchema.components.schemas.GenomicVariantCreate;

        const properties = schema.properties as Record<string, any>;
        const propertySchema = properties?.[propertyName]?.anyOf?.[0];
        
        if (!propertySchema) {
            console.error(`Property '${propertyName}' not found in schema`);
            return '.*';
        }
        
        if (propertySchema.type === 'string' && propertySchema.pattern) {
            return propertySchema.pattern;
        }
        
        console.warn(`No regex pattern found for property '${propertyName}'`);
        return '.*';
    }
      

}