import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { Dna } from 'lucide-angular';

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
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  RadioSelectComponent,
  MultiReferenceSelectComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { Fieldset } from 'primeng/fieldset';
import { Divider } from 'primeng/divider';

@Component({
  standalone: true,
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
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class GenomicVariantFormComponent extends AbstractFormBase implements OnInit {

    private readonly genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: GenomicVariantCreate) => this.genomicVariantsService.createGenomicVariant({genomicVariantCreate: payload});
    public readonly updateService = (id: string, payload: GenomicVariantCreate) => this.genomicVariantsService.updateGenomicVariant({genomicVariantId: id, genomicVariantCreate: payload});

    public readonly title: string = 'Genomic variant';
    public readonly subtitle: string = 'Add new genomic variant';
    public readonly icon = Dna;

    private caseId!: string;
    public initialData: GenomicVariantCreate | any = {};
    

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

    ngOnInit() {
        // Construct the form 
        this.constructForm();
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            date: [this.initialData?.date, Validators.required],
            genePanel: [this.initialData?.genePanel],      
            assessment: [this.initialData?.assessment],      
            confidence: [this.initialData?.confidence],      
            analysisMethod: [this.initialData?.analysisMethod, Validators.required],  
            clinicalRelevance: [this.initialData?.clinicalRelevance], 
            genes: [this.initialData?.genes,Validators.required],     
            dnaHgvs: [this.initialData?.dnaHgsv, [Validators.required, Validators.pattern(this.extractRegexPattern('dnaHgvs'))]],         
            rnaHgvs: [this.initialData?.rnaHgsv, Validators.pattern(this.extractRegexPattern('rnaHgvs'))],         
            proteinHgvs: [this.initialData?.proteinHgvs, Validators.pattern(this.extractRegexPattern('proteinHgvs'))],         
            copyNumber: [this.initialData?.copyNumber],       
            molecularConsequence: [this.initialData?.molecularConsequence],        
            alleleFrequency: [this.initialData?.alleleFrequency],  
            alleleDepth: [this.initialData?.alleleDepth],       
            zygosity: [this.initialData?.zygosity],        
            inheritance: [this.initialData?.inheritance],        
            clinvar: [this.initialData?.clinvar],             
        });
    }


    constructAPIPayload(data: any): GenomicVariantCreate {   
        return {
            caseId: this.caseId,
            date: data.date,
            genes: data.genes,
            genePanel: data.genePanel,            
            assessment: data.assessment,            
            confidence: data.confidence,            
            analysisMethod: data.analysisMethod,   
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