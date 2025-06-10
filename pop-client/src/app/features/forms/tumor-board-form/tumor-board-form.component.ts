import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { forkJoin, map } from 'rxjs';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { Fieldset } from 'primeng/fieldset';
import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectModule } from 'primeng/select';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputMaskModule } from 'primeng/inputmask';

import { 
    NeoplasticEntitiesService,
    GenomicVariantsService,
    GenomicVariant,
    TumorMarkersService,
    GenomicSignaturesService,
    AnyTumorBoard,
    TumorBoardsService,
    UnspecifiedTumorBoardCreate,
    MolecularTherapeuticRecommendation,
    MolecularTherapeuticRecommendationCreate,
    CodedConcept,
    MolecularTumorBoardCreate,
    AnyGenomicSignature,
    TumorMarker,
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent,
  RadioChoice,
  MultiReferenceSelectComponent,
  RadioSelectComponent
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';


export type AnyTumorBoardCreate = UnspecifiedTumorBoardCreate | MolecularTumorBoardCreate;
export type TumorTypeCategory = "molecular" | "unspecified";


@Component({
    selector: 'tumor-board-form',
    templateUrl: './tumor-board-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        SelectModule,
        MultiSelectModule,
        DatePickerComponent,
        Fluid,
        Fieldset,
        MultiReferenceSelectComponent,
        InputMaskModule,
        ButtonModule,
        ConceptSelectorComponent,
        RadioSelectComponent,
        FormControlErrorComponent,
    ]
})
export class TumorBoardFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<AnyTumorBoard>();

    // Service injections
    readonly #tumorBoardsService: TumorBoardsService = inject(TumorBoardsService);
    readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #genomicVariantsService: GenomicVariantsService = inject(GenomicVariantsService);
    readonly #tumorMarkersService: TumorMarkersService = inject(TumorMarkersService);
    readonly #genomicSignaturesService: GenomicSignaturesService = inject(GenomicSignaturesService);
    readonly #fb = inject(FormBuilder);
    

    // Create and update service methods for the form data
    public readonly createService = (payload: AnyTumorBoardCreate) => this.#tumorBoardsService.createTumorBoard({payload1: payload as any});
    public readonly updateService = (id: string, payload: AnyTumorBoardCreate) => this.#tumorBoardsService.updateTumorBoardById({tumorBoardId: id, payload1: payload as any});
    override readonly subformsServices = [
        {
            condition: this.molecularTherapeuticRecommendationsCondition.bind(this),
            payloads: this.molecularBoardRecommendationsPayloads.bind(this),
            deletedEntries: this.getdeletedMolecularTherapeuticRecommendations.bind(this),
            delete: (parentId: string, id: string) => this.#tumorBoardsService.deleteMolecularTherapeuticRecommendation({tumorBoardId: parentId, recommendationId: id}),
            create: (parentId: string, payload: MolecularTherapeuticRecommendationCreate) => this.#tumorBoardsService.createMolecularTherapeuticRecommendation({tumorBoardId: parentId, molecularTherapeuticRecommendationCreate: payload}),
            update: (parentId: string, id: string, payload: MolecularTherapeuticRecommendationCreate) => this.#tumorBoardsService.updateMolecularTherapeuticRecommendation({tumorBoardId: parentId, recommendationId: id, molecularTherapeuticRecommendationCreate: payload}),
        },
    ]
    #deletedMolecularRecommendations: string[] = [];

    // Define the main form
    public form = this.#fb.group({
        category: this.#fb.control<TumorTypeCategory | null>('unspecified', Validators.required),
        date: this.#fb.control<string | null>(null, Validators.required),
        relatedEntities: this.#fb.control<string[] | null>(null, Validators.required),
        recommendations: this.#fb.control<CodedConcept[]>([]),
        molecularBoard: this.#fb.group({
            conductedMolecularComparison: this.#fb.control<boolean | null>(null),
            succeededMolecularComparison: this.#fb.control<boolean | null>(null),
            molecularComparisonMatch: this.#fb.control<string | null>(null),
            conductedCupCharacterization: this.#fb.control<boolean | null>(null),
            characterizedCup: this.#fb.control<boolean | null>(null),
            reviewedReports: this.#fb.control<string[] | null>(null),
            therapeuticRecommendations: this.#fb.array<FormGroup>([]),
        }),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
      
        this.form.patchValue({
          category: data.category ?? 'unspecified',
          date: data.date ?? null,
          relatedEntities: data.relatedEntitiesIds ?? null,
          recommendations: data.recommendations ?? [],
        });
      
        this.form.get('molecularBoard')?.patchValue({
            conductedMolecularComparison: data.conductedMolecularComparison ?? null,
            succeededMolecularComparison: data.molecularComparisonMatchId ? true : null,
            molecularComparisonMatch: data.molecularComparisonMatchId ?? null,
            conductedCupCharacterization: data.conductedMolecularComparison ?? null,
            characterizedCup: data.characterizedCup ?? null,
            reviewedReports: data.reviewedReports ?? null,
            therapeuticRecommendations: []
        });
      
        (data.therapeuticRecommendations ?? []).forEach((initialData: MolecularTherapeuticRecommendation) => {
          let subform = this.#molecularBoardRecommendationForm(initialData);
          subform = this.changeTherapeuticRecommendationValidation(subform, subform.value.recommendationType);
          this.form.controls.molecularBoard.controls.therapeuticRecommendations.push(subform)
        });
        
      });    

    //Definition for the dynamic subform constructor
    #molecularBoardRecommendationForm = (initialData: MolecularTherapeuticRecommendation) => {
        const subform = this.#fb.group({
            id: this.#fb.control<string | null>(
                initialData?.id ?? null 
            ),
            expectedEffect: this.#fb.control<CodedConcept | null>(
                initialData?.expectedEffect ?? null, 
                Validators.required
            ),
            recommendationType: this.#fb.control<string | null>(
            initialData?.drugs?.length as number > 0
                ? this.TherapeuticRecommendationType.Drugs
                : (initialData?.clinicalTrial
                ? this.TherapeuticRecommendationType.ClinicalTrial
                : this.TherapeuticRecommendationType.Drugs)
            ),
            clinicalTrial: this.#fb.control<string | null>(
                initialData?.clinicalTrial ?? null, 
            ),
            offLabelUse: this.#fb.control<boolean | null>(
                initialData?.offLabelUse ?? null, 
            ),
            withinSoc: this.#fb.control<boolean | null>(
                initialData?.withinSoc ?? null, 
            ),
            drugs: this.#fb.control<CodedConcept[]>(
                initialData?.drugs ?? [], Validators.required
            ),
            supportingEntries: this.#fb.control<string[] | null>(
            [...initialData?.supportingGenomicVariantsIds || [], ...initialData?.supportingGenomicSignaturesIds || [], ...initialData?.supportingTumorMarkersIds || []],
            Validators.required
            ),
        })
        subform.controls['recommendationType'].valueChanges.subscribe(
            (recommendationType) => this.changeTherapeuticRecommendationValidation(subform, recommendationType)
        )
        return subform
    }


    readonly payload = (): AnyTumorBoardCreate | undefined => {
        const data = this.form.value;    
        const payload = {
            caseId: this.caseId(),
            category: data.category!,
            date: data.date!,
            relatedEntitiesIds: data.relatedEntities!,
            recommendations: data.recommendations,
        };
        switch (data.category) {
            case 'unspecified':
                return payload as UnspecifiedTumorBoardCreate;
            case 'molecular':
                const mtb = data.molecularBoard!
                return {
                    ...payload,
                    conductedMolecularComparison: mtb.conductedMolecularComparison,
                    molecularComparisonMatchId: mtb.conductedMolecularComparison ? (mtb.succeededMolecularComparison ? mtb.molecularComparisonMatch: null) : null,
                    conductedCupCharacterization: mtb.conductedCupCharacterization,
                    characterizedCup: mtb.conductedCupCharacterization ? mtb.characterizedCup: null,
                    reviewedReports: mtb.reviewedReports!,
                }  as MolecularTumorBoardCreate
            default:
                return undefined
                
        } 
    }

    private molecularBoardRecommendationsPayloads(): MolecularTherapeuticRecommendationCreate[] {
        const data = this.form.value.molecularBoard;
        return data!.therapeuticRecommendations!.map((subformData: any) => {return {
            id: subformData.id,
            expectedEffect: subformData.expectedEffect,
            clinicalTrial: subformData.clinicalTrial, 
            offLabelUse: subformData.offLabelUse, 
            withinSoc: subformData.withinSoc, 
            drugs: subformData.drugs, 
            supportingGenomicVariantsIds: subformData.supportingEntries.filter((entryId: string) =>  this.#molecularEvidenceVariantsIds().includes(entryId)),
            supportingGenomicSignaturesIds: subformData.supportingEntries.filter((entryId:any) => this.#molecularEvidenceSignaturesIds().includes(entryId)),
            supportingTumorMarkersIds: subformData.supportingEntries.filter((entryId:any) => this.#molecularEvidenceMerkersIds().includes(entryId)),
        }})
    }

    #molecularEvidenceVariantsIds = computed( () => this.molecularEvidence.value()!.filter((entry) => this.#isGenomicVariant(entry))?.map((entry) => entry.id))
    #molecularEvidenceSignaturesIds = computed( () => this.molecularEvidence.value()!.filter((entry) => this.#isGenomicSignature(entry))?.map((entry) => entry.id))
    #molecularEvidenceMerkersIds = computed( () => this.molecularEvidence.value()!.filter((entry) => this.#isTumorMarker(entry))?.map((entry) => entry.id))
    #isGenomicVariant(obj: any): obj is GenomicVariant {
        return typeof obj === 'object' && obj !== null
          && obj.hasOwnProperty('genes')
          && obj.hasOwnProperty('isPathogenic');
    }
    #isGenomicSignature(obj: any): obj is AnyGenomicSignature {
        return typeof obj === 'object' && obj !== null
        && obj.hasOwnProperty('category') && typeof obj.category === 'string';
    }
    #isTumorMarker(obj: any): obj is TumorMarker {
        return typeof obj === 'object' && obj !== null
        && obj.hasOwnProperty('analyte') && typeof obj.analyte === 'string';
    }

    // All neoplastic entities related to this patient case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    });

    // All primary neoplastic entities related to this patient case
    public relatedPrimaryEntities = rxResource({
        request: () => ({caseId: this.caseId(), relationship: 'primary'}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    }); 

    // All genomic panels/reports potentially discussed in the molecular tumor board for a case
    public relatedReports = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#genomicVariantsService.getGenomicVariants(request).pipe(map( (response) => {
            return Array.from(new Set(response.items.map((variant: GenomicVariant) => {
                const entry = `${variant.genePanel ?? 'Unknown test'} (${variant.date})`;
                return {name: entry, value: entry}
            })))
        }))
    }); 

    // All molecular findings that could be used as evidence in the molecular tumor board
    public molecularEvidence = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => forkJoin([
            this.#genomicVariantsService.getGenomicVariants(request).pipe(map((response) => response.items)),
            this.#genomicSignaturesService.getGenomicSignatures(request).pipe(map((response) => response.items)),
            this.#tumorMarkersService.getTumorMarkers(request).pipe(map((response) => response.items)
        )]).pipe(
            map(([genomicVariants, genomicSignatures, tumorMarkers]) => {
                return [...genomicVariants, ...genomicSignatures, ...tumorMarkers];
            })
        )
    }); 

    // Human readable choices for UI elements
    public readonly tumorBoardSpecialtyChoices: RadioChoice[] = [
        { name: 'Unspecified', value: 'unspecified' },
        { name: 'Molecular tumor board', value: 'molecular' },
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

    public addMolecularTherapeuticRecommendation() {
        this.form.controls['molecularBoard'].controls['therapeuticRecommendations'].push(this.#molecularBoardRecommendationForm({} as MolecularTherapeuticRecommendation));
    }

    public removeMolecularTherapeuticRecommendation(index: number) {
        const recommendationsArray = this.form.controls['molecularBoard'].controls['therapeuticRecommendations']
        const recommendation = recommendationsArray.value[index];
        if (recommendation?.id) {
            this.#deletedMolecularRecommendations.push(recommendation.id);
        }
        recommendationsArray.removeAt(index);
    }

    private getdeletedMolecularTherapeuticRecommendations(): string[] {
        return this.#deletedMolecularRecommendations;
    }

    private molecularTherapeuticRecommendationsCondition(): boolean {
        return this.form.value.category === 'molecular';
    }

    // public addMolecularTherapeuticRecommendation() {
    //     const newSubform = this.constructMolecularTherapeuticRecommendationSubForm({} as MolecularTherapeuticRecommendation);
    //     newSubform.get('recommendationType')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((category: any) => {
    //         const fieldNames = [
    //             'clinicalTrial', 
    //             'expectedEffect', 
    //             'offLabelUse', 
    //             'withinSoc',
    //             'drugs',
    //         ];
    //         fieldNames.forEach(
    //             (field: string) => {
    //                 newSubform.get(field)?.setValidators([])
    //                 newSubform.get(field)?.setValue(null)
    //                 newSubform.get(field)?.updateValueAndValidity()
    //             }
    //         );
    //         this.changeTherapeuticRecommendationValidation(newSubform, category);
    //     })
    //     this.changeTherapeuticRecommendationValidation(newSubform, newSubform.value.recommendationType);
    //     this.molecularTherapeuticRecommendationsFormArray.push(newSubform);
    // }




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
        return form
    }

}