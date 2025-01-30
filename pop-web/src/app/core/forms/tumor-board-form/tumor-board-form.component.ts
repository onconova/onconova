import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators, FormArray, FormControl } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { forkJoin, map, Observable } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import * as moment from 'moment'; 

import { Presentation } from 'lucide-angular';

import { Fieldset } from 'primeng/fieldset';
import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputMaskModule } from 'primeng/inputmask';

import { 
    NeoplasticEntitiesService,
    NeoplasticEntity,
    GenomicVariantsService,
    GenomicVariantSchema,
    TumorMarkersService,
    TumorMarker,
    GenomicSignaturesService,
    AnyGenomicSignature,
    AnyTumorBoard,
    TumorBoardsService,
    UnspecifiedTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema,
    MolecularTherapeuticRecommendationCreateSchema,
} from '../../../shared/openapi'

import { 
  CodedConceptSelectComponent, 
  MaskedCalendarComponent,
  ControlErrorComponent,
  RadioChoice,
  ReferenceMultiSelect,
  RadioSelectComponent
} from '../../forms/components';

import { AbstractFormBase } from '../abstract-form-base.component';

const TumorBoardSpecialties = {
    Molecular: 'molecular',
    Unspecified: 'unspecified',
}

export type AnyTumorBoardCreateSchema = UnspecifiedTumorBoardCreateSchema | MolecularTherapeuticRecommendationCreateSchema;

@Component({
  standalone: true,
  selector: 'tumor-board-form',
  templateUrl: './tumor-board-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    SelectModule,
    MultiSelectModule,
    MaskedCalendarComponent,
    Fluid,
    Fieldset,
    ReferenceMultiSelect,
    InputNumber,
    InputMaskModule,
    ButtonModule,
    CodedConceptSelectComponent,
    RadioSelectComponent,
    ControlErrorComponent,
  ],
})
export class TumorBoardFormComponent extends AbstractFormBase implements OnInit {

    private readonly tumorBoardsService: TumorBoardsService = inject(TumorBoardsService);
    private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    private readonly genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    private readonly tumorMarkersService: TumorMarkersService = inject(TumorMarkersService);
    private readonly genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: AnyTumorBoardCreateSchema) => this.tumorBoardsService.createTumorBoard({payload1: payload as any});
    public readonly updateService = (id: string, payload: AnyTumorBoardCreateSchema) => this.tumorBoardsService.updateTumorBoardById({tumorBoardId: id, payload1: payload as any});
    override readonly subformsServices = [
        {
            condition: (data: any) => data.category === TumorBoardSpecialties.Molecular,
            payloads: this.constructMolecularTherapeuticRecommendationPayloads.bind(this),
            deletedEntries: this.getdeletedMolecularTherapeuticRecommendations.bind(this),
            delete: (parentId: string, id: string) => this.tumorBoardsService.deleteMolecularTherapeuticRecommendation({tumorBoardId: parentId, recommendationId: id}),
            create: (parentId: string, payload: MolecularTherapeuticRecommendationCreateSchema) => this.tumorBoardsService.createMolecularTherapeuticRecommendation({tumorBoardId: parentId, molecularTherapeuticRecommendationCreateSchema: payload}),
            update: (parentId: string, id: string, payload: MolecularTherapeuticRecommendationCreateSchema) => this.tumorBoardsService.updateMolecularTherapeuticRecommendation({tumorBoardId: parentId, recommendationId: id, molecularTherapeuticRecommendationCreateSchema: payload}),
        },
    ]
    private deletedMolecularTherapeuticRecommendations: string[] = [];

    public readonly title: string = 'Tumor Board';
    public readonly subtitle: string = 'Add new tumor board';
    public readonly icon = Presentation;

    private caseId!: string;
    public molecularTherapeuticRecommendationsFormArray!: FormArray;
    public initialData: AnyTumorBoard | any = {};
    public relatedEntities$!: Observable<NeoplasticEntity[]>;
    public relatedPrimaryEntities$!: Observable<NeoplasticEntity[]>; 
    public relatedEvidence$!: Observable<(GenomicVariantSchema | TumorMarker | AnyGenomicSignature)[]>;
    public relatedReports$!: Observable<RadioChoice[]>;

    public readonly TumorBoardSpecialties = TumorBoardSpecialties;
    public readonly tumorBoardSpecialtyChoices: RadioChoice[] = [
        { name: 'Unspecified', value: TumorBoardSpecialties.Unspecified },
        { name: 'Molecular tumor board', value: TumorBoardSpecialties.Molecular },
    ];

    public readonly TherapeuticRecommendationType = {
        Drugs: 'drugs',
        ClinicalTrial: 'clinical-trial'
    };
    public readonly TherapeuticRecommendationTypeChoices: RadioChoice[] = [
        { name: 'Medication(s)', value: this.TherapeuticRecommendationType.Drugs },
        { name: 'Clinical Trial(s)', value: this.TherapeuticRecommendationType.ClinicalTrial },
    ]

    public readonly YesNoChoices: RadioChoice[] = [
        { name: 'Unknown', value: null },
        { name: 'Yes', value: true },
        { name: 'No', value: false },
    ]

    ngOnInit() {
        // Construct the form 
        this.constructForm()
        this.relatedEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities({caseId: this.caseId}).pipe(map((response) => response.items))
        this.relatedPrimaryEntities$ = this.neoplasticEntitiesService.getNeoplasticEntities({caseId: this.caseId, relationship: 'primary'}).pipe(map((response) => response.items))
        this.relatedReports$ = this.genomicVariantsService.getGenomicVariants({caseId:this.caseId}).pipe(map( (response) => {
            return Array.from(new Set(response.items.map((variant: GenomicVariantSchema) => {
                const entry = `${variant.genePanel || 'Unknown test'} (${variant.date})`;
                return {name: entry, value: entry}
            })))
        }));
        this.relatedEvidence$ = forkJoin(
            this.genomicVariantsService.getGenomicVariants({caseId:this.caseId}).pipe(map((response) => response.items)),
            this.genomicSignaturesService.getGenomicSignatures({caseId:this.caseId}).pipe(map((response) => response.items)),
            this.tumorMarkersService.getTumorMarkers({caseId:this.caseId}).pipe(map((response) => response.items)),
        ).pipe(
            map(([genomicVariants, genomicSignatures, tumorMarkers]) => {
                return [...genomicVariants, ...genomicSignatures, ...tumorMarkers];
            })
        )

        this.form.get('category')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(category => {
            
            const molecularTumorBoardFields = [
                'conductedMolecularComparison', 
                'molecularComparisonMatch', 
                'conductedCupCharacterization', 
                'succeededMolecularComparison',
                'characterizedCup',
                'reviewedReports',
            ];
            const fieldNames = [...molecularTumorBoardFields];
            fieldNames.forEach(
                (field: string) => {
                    this.form.get(field)?.setValidators([])
                    this.form.get(field)?.setValue(null)
                    this.form.get(field)?.updateValueAndValidity()
                }
            );
            switch (category) {
                case TumorBoardSpecialties.Unspecified:
                    break;
                case TumorBoardSpecialties.Molecular:
                    break;
            }
            fieldNames.forEach((field: string) => this.form.get(field)?.updateValueAndValidity())
        })
    }

    constructForm(): void {

        this.molecularTherapeuticRecommendationsFormArray = this.formBuilder.array((this.initialData?.therapeuticRecommendations || [])?.map(
            (initialRecommendation: MolecularTherapeuticRecommendationSchema) => {
                console.log('initialRecommendation',initialRecommendation)
                const subform = this.constructMolecularTherapeuticRecommendationSubForm(initialRecommendation);
                this.changeTherapeuticRecommendationValidation(subform, subform.value.recommendationType)
                return subform
            }
        ))


        this.form = this.formBuilder.group({
            category: [this.initialData?.category || TumorBoardSpecialties.Unspecified, Validators.required],
            date: [this.initialData?.date, Validators.required],
            relatedEntities: [this.initialData?.relatedEntitiesIds, Validators.required],
            recommendations: [this.initialData?.recommendations],
            // Molecular tumor board specific
            conductedMolecularComparison: [this.initialData?.conductedMolecularComparison],
            succeededMolecularComparison: [this.initialData?.molecularComparisonMatchId ? true : null],
            molecularComparisonMatch: [this.initialData?.molecularComparisonMatchId],
            conductedCupCharacterization: [this.initialData?.conductedMolecularComparison],
            characterizedCup: [this.initialData?.characterizedCup],
            reviewedReports: [this.initialData?.reviewedReports],
            therapeuticRecommendations: this.molecularTherapeuticRecommendationsFormArray,
        });
    }


    constructMolecularTherapeuticRecommendationSubForm(initalData: MolecularTherapeuticRecommendationSchema | null ) {
        return this.formBuilder.group({
            id: [initalData?.id],
            expectedEffect: [initalData?.expectedEffect, Validators.required],
            recommendationType: [initalData?.drugs?.length as number > 0 ? this.TherapeuticRecommendationType.Drugs : (initalData?.clinicalTrial ? this.TherapeuticRecommendationType.ClinicalTrial : this.TherapeuticRecommendationType.Drugs)],
            clinicalTrial: [initalData?.clinicalTrial, Validators.required],
            offLabelUse: [initalData?.offLabelUse, Validators.required],
            withinSoc: [initalData?.withinSoc, Validators.required],
            drugs: [initalData?.drugs, Validators.required],
            supportingEntries:[[...initalData?.supportingGenomicVariantsIds || [], ...initalData?.supportingGenomicSignaturesIds || [], ...initalData?.supportingTumorMarkersIds || []], Validators.required],
        })
    }

    constructAPIPayload(data: any): AnyTumorBoardCreateSchema {    
        let additionalData: object = {}
        switch (data.category) {
            case TumorBoardSpecialties.Unspecified:
                break;
            case TumorBoardSpecialties.Molecular:
                additionalData = {
                    conductedMolecularComparison: data.conductedMolecularComparison,
                    molecularComparisonMatchId: data.conductedMolecularComparison ? (data.succeededMolecularComparison ? data.molecularComparisonMatch: null) : null,
                    conductedCupCharacterization: data.conductedCupCharacterization,
                    characterizedCup: data.conductedCupCharacterization ? data.characterizedCup: null,
                    reviewedReports: data.reviewedReports,
                }
                break;
        } 
        return {
            caseId: this.caseId,
            category: data.category,
            date: moment(data.date, ['DD/MM/YYYY','YYYY-MM-DD'], true).format('YYYY-MM-DD'),
            relatedEntitiesIds: data.relatedEntities,
            recommendations: data.recommendations,
            ...additionalData
        };
    }

    private constructMolecularTherapeuticRecommendationPayloads(data: any): MolecularTherapeuticRecommendationCreateSchema {
        return data.therapeuticRecommendations.map((subformData: any) => {return {
            id: subformData.id,
            expectedEffect: subformData.expectedEffect,
            clinicalTrial: subformData.clinicalTrial, 
            offLabelUse: subformData.offLabelUse, 
            withinSoc: subformData.withinSoc, 
            drugs: subformData.drugs, 
            supportingGenomicVariantsIds: subformData.supportingEntries.filter((entryId:any) => entryId.includes('GenomicVariant')),
            supportingGenomicSignaturesIds: subformData.supportingEntries.filter((entryId:any) => entryId.includes('GenomicSignature')),
            supportingTumorMarkersIds: subformData.supportingEntries.filter((entryId:any) => entryId.includes('TumorMarker')),
        }})
    }

    public addMolecularTherapeuticRecommendation() {
        const newSubform = this.constructMolecularTherapeuticRecommendationSubForm({} as MolecularTherapeuticRecommendationSchema);
        newSubform.get('recommendationType')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((category: any) => {
            const fieldNames = [
                'clinicalTrial', 
                'expectedEffect', 
                'offLabelUse', 
                'withinSoc',
                'drugs',
            ];
            fieldNames.forEach(
                (field: string) => {
                    newSubform.get(field)?.setValidators([])
                    newSubform.get(field)?.setValue(null)
                    newSubform.get(field)?.updateValueAndValidity()
                }
            );
            this.changeTherapeuticRecommendationValidation(newSubform, category);
        })
        this.changeTherapeuticRecommendationValidation(newSubform, newSubform.value.recommendationType);
        this.molecularTherapeuticRecommendationsFormArray.push(newSubform);
    }

    public removeMolecularTherapeuticRecommendation(index: number) {
        const settingValue = this.molecularTherapeuticRecommendationsFormArray.value[index];
        if (settingValue?.id) {
            this.deletedMolecularTherapeuticRecommendations.push(settingValue.id);
        }
        this.molecularTherapeuticRecommendationsFormArray.removeAt(index);
    }

    private getdeletedMolecularTherapeuticRecommendations(): string[] {
        return this.deletedMolecularTherapeuticRecommendations;
    }

    private changeTherapeuticRecommendationValidation(form: any, category: any) {
        const fieldNames = [
            'clinicalTrial', 
            'expectedEffect', 
            'offLabelUse', 
            'withinSoc',
            'drugs',
        ];
        fieldNames.forEach(
            (field: string) => {
                form.get(field)?.setValidators([])
            }
        );
        console.log('VALIDATORS', category)
        switch (category) {
            case this.TherapeuticRecommendationType.Drugs:
                fieldNames.filter(field => field!='clinicalTrial').forEach(
                    (field: string) => {
                        form.get(field)?.setValidators([Validators.required])
                    }
                );
                break;
            case this.TherapeuticRecommendationType.ClinicalTrial:
                form.get('clinicalTrial')?.setValidators([Validators.required])
                break;
        }
        fieldNames.forEach((field: string) => form.get(field)?.updateValueAndValidity())
    }

}