import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { Dna } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';

import { 
    GenomicVariantCreateSchema,
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
    Fluid,
    InputNumber,
    InputTextModule,
    ButtonModule,
    MultiReferenceSelectComponent,
    ConceptSelectorComponent,
    RadioSelectComponent,
    FormControlErrorComponent,
  ],
})
export class GenomicVariantFormComponent extends AbstractFormBase implements OnInit {

    private readonly genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: GenomicVariantCreateSchema) => this.genomicVariantsService.createGenomicVariant({genomicVariantCreateSchema: payload});
    public readonly updateService = (id: string, payload: GenomicVariantCreateSchema) => this.genomicVariantsService.updateGenomicVariant({genomicVariantId: id, genomicVariantCreateSchema: payload});

    public readonly title: string = 'Genomic variant';
    public readonly subtitle: string = 'Add new genomic variant';
    public readonly icon = Dna;

    private caseId!: string;
    public initialData: GenomicVariantCreateSchema | any = {};
    

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
            analysisMethod: [this.initialData?.analysisMethod],  
            clinicalRelevance: [this.initialData?.clinicalRelevance], 
            genes: [this.initialData?.genes,Validators.required],     
            chromosomes: [this.initialData?.chromosomes],     
            cytogeneticLocation: [this.initialData?.cytogeneticLocation,Validators.pattern('^([1-9]|1[0-9]|2[0-2]|X|Y)([pq])(\\d+)(\\d+)(?:\\.(\\d+))?$')],     
            genomeAssemblyVersion: [this.initialData?.genomeAssemblyVersion],   
            genomicRefseq: [this.initialData?.genomicRefseq, Validators.pattern('^(NG|NC|LRG)(.*)$')],      
            transcriptRefseq: [this.initialData?.transcriptRefseq, Validators.pattern('^(NM|NG|ENST|LRG)(.*)$')],      
            codingHgsv: [this.initialData?.codingHgsv, Validators.pattern('^(.*):c\\.(.*)$')],         
            proteinHgvs: [this.initialData?.proteinHgvs, Validators.pattern('^(.*):p\\.(.*)$')],         
            genomicHgvs: [this.initialData?.genomicHgvs, Validators.pattern('^(.*):g\\.(.*)$')],         
            dnaChangeType: [this.initialData?.dnaChangeType],         
            aminoacidChangeType: [this.initialData?.aminoacidChangeType],         
            molecularConsequence: [this.initialData?.molecularConsequence],        
            alleleFrequency: [this.initialData?.alleleFrequency],       
            copyNumber: [this.initialData?.copyNumber],       
            alleleDepth: [this.initialData?.alleleDepth],       
            zygosity: [this.initialData?.zygosity],        
            inheritance: [this.initialData?.inheritance],        
            coordinateSystem: [this.initialData?.coordinateSystem],        
            exactGenomicCoordinatesStart: [this.initialData?.exactGenomicCoordinates?.start],             
            exactGenomicCoordinatesEnd: [this.initialData?.exactGenomicCoordinates?.end],             
            innerGenomicCoordinatesStart: [this.initialData?.innerGenomicCoordinates?.start],             
            innerGenomicCoordinatesEnd: [this.initialData?.innerGenomicCoordinates?.end],             
            outerGenomicCoordinatesStart: [this.initialData?.outerGenomicCoordinates?.start],             
            outerGenomicCoordinatesEnd: [this.initialData?.outerGenomicCoordinates?.end],             
            clinvar: [this.initialData?.clinvar],             
        });
    }


    constructAPIPayload(data: any): GenomicVariantCreateSchema {    
        return {
            caseId: this.caseId,
            date: data.date,
            genes: data.genes,
            chromosomes: data.chromosomes,
            genePanel: data.genePanel,            
            assessment: data.assessment,            
            confidence: data.confidence,            
            analysisMethod: data.analysisMethod,   
            clinicalRelevance: data.clinicalRelevance,   
            cytogeneticLocation: data.cytogeneticLocation,   
            genomeAssemblyVersion: data.genomeAssemblyVersion,   
            genomicRefseq: data.genomicRefseq,   
            transcriptRefseq: data.transcriptRefseq,   
            codingHgvs: data.codingHgsv,   
            proteinHgvs: data.proteinHgsv,   
            genomicHgvs: data.genomicHgsv,   
            dnaChangeType: data.dnaChangeType,   
            aminoacidChangeType: data.aminoacidChangeType,   
            molecularConsequence: data.molecularConsequence,   
            coordinateSystem: data.coordinateSystem,    
            exactGenomicCoordinates: data.exactGenomicCoordinatesStart && data.exactGenomicCoordinatesEnd ? {start: data.exactGenomicCoordinatesStart, end: data.exactGenomicCoordinatesEnd}: null,   
            innerGenomicCoordinates: data.innerGenomicCoordinatesStart && data.innerGenomicCoordinatesEnd ? {start: data.innerGenomicCoordinatesStart, end: data.innerGenomicCoordinatesEnd}: null,  
            outerGenomicCoordinates: data.outerGenomicCoordinatesStart && data.outerGenomicCoordinatesEnd ? {start: data.outerGenomicCoordinatesStart, end: data.outerGenomicCoordinatesEnd}: null, 
            clinvar: data.clinvar,    
            alleleFrequency: data.alleleFrequency,   
            copyNumber: data.copyNumber,   
            alleleDepth: data.alleleDepth,   
            zygosity: data.zygosity,   
            inheritance: data.inheritance        
        };
    }

}