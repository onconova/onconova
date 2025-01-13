import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { Dna } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';

import { 
    GenomicVariantCreateSchema,
    GenomicVariantsService,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent,
  RadioChoice,
  RadioSelectComponent,
  ReferenceMultiSelect,
} from '../../forms/components';

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
    MaskedCalendarComponent,
    Fluid,
    InputNumber,
    ButtonModule,
    ReferenceMultiSelect,
    CodedConceptSelectComponent,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class GenomicVariantFormComponent extends AbstractFormBase implements OnInit {

    private readonly genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = this.genomicVariantsService.createGenomicVariant.bind(this.genomicVariantsService);
    public readonly updateService = this.genomicVariantsService.updateGenomicVariant.bind(this.genomicVariantsService);

    public readonly title: string = 'Genomic variant';
    public readonly subtitle: string = 'Add new genomic variant';
    public readonly icon = Dna;

    private caseId!: string;
    public initialData: GenomicVariantCreateSchema | any = {};
    

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
            cytogeneticLocation: [this.initialData?.cytogeneticLocation],     
            genomeAssemblyVersion: [this.initialData?.genomeAssemblyVersion],   
            genomicRefseq: [this.initialData?.genomicRefseq],      
            transcriptRefseq: [this.initialData?.transcriptRefseq],      
            codingHgsv: [this.initialData?.codingHgsv],         
            proteinHgsv: [this.initialData?.proteinHgsv],         
            genomicHgsv: [this.initialData?.genomicHgsv],         
            dnaChangeType: [this.initialData?.dnaChangeType],         
            aminoacidChangeType: [this.initialData?.aminoacidChangeType],         
            molecularConsequence: [this.initialData?.molecularConsequence],        
            alleleFrequency: [this.initialData?.alleleFrequency],       
            copyNumber: [this.initialData?.copyNumber],       
            alleleDepth: [this.initialData?.alleleDepth],       
            zygosity: [this.initialData?.zygosity],        
            inheritance: [this.initialData?.inheritance],        
            coordinateSystem: [this.initialData?.coordinateSystem],        
            exactGenomicCoordinates: [this.initialData?.exactGenomicCoordinates],             
            innerGenomicCoordinates: [this.initialData?.innerGenomicCoordinates],             
            outerGenomicCoordinates: [this.initialData?.outerGenomicCoordinates],             
            clinvar: [this.initialData?.clinvar],             
        });
    }


    constructAPIPayload(data: any): GenomicVariantCreateSchema {    
        return {
            caseId: this.caseId,
            date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
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
            codingHgsv: data.codingHgsv,   
            proteinHgsv: data.proteinHgsv,   
            genomicHgsv: data.genomicHgsv,   
            dnaChangeType: data.dnaChangeType,   
            aminoacidChangeType: data.aminoacidChangeType,   
            molecularConsequence: data.molecularConsequence,   
            coordinateSystem: data.coordinateSystem,    
            exactGenomicCoordinates: data.exactGenomicCoordinates,    
            innerGenomicCoordinates: data.innerGenomicCoordinates,    
            outerGenomicCoordinates: data.outerGenomicCoordinates,    
            clinvar: data.clinvar,    
            alleleFrequency: data.alleleFrequency,   
            copyNumber: data.copyNumber,   
            alleleDepth: data.alleleDepth,   
            zygosity: data.zygosity,   
            inheritance: data.inheritance        
        };
    }

}