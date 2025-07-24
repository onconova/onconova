import { Component, computed, effect, inject, input,signal,ViewEncapsulation } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectButton } from 'primeng/selectbutton';
import { Tooltip } from 'primeng/tooltip';
import { RadioButton } from 'primeng/radiobutton';

import { 
  NeoplasticEntitiesService, 
  TumorMarkerCreate,
  TumorMarkersService,
  AnalyteResultType,
  TumorMarkerPresenceChoices,
  TumorMarkerImmuneCellScoreChoices,
  TumorMarkerTumorProportionScoreChoices,
  TumorMarkerImmunohistochemicalScoreChoices,
  TumorMarkerNuclearExpressionStatusChoices,
  TerminologyService,
  CodedConcept,
  TumorMarker,
  Measure,
} from 'pop-api-client'

import { 
  DatePickerComponent,
  FormControlErrorComponent ,
  MeasureInputComponent,
  MultiReferenceSelectComponent,
  RadioSelectComponent, 
  RadioChoice
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

const valueTypeMap = {
  immuneCellScore: AnalyteResultType.ImmuneCellsScore,
  tumorProportionScore: AnalyteResultType.TumorProportionScore,
  combinedPositiveScore: AnalyteResultType.CombinedPositiveScore,
  massConcentration: AnalyteResultType.MassConcentration,
  substanceConcentration: AnalyteResultType.SubstanceConcentration,
  arbitraryConcentration: AnalyteResultType.ArbitraryConcentration,
  fraction: AnalyteResultType.Fraction,
  immunohistochemicalScore: AnalyteResultType.ImmunoHistoChemicalScore,
  presence: AnalyteResultType.Presence,
  nuclearExpressionStatus: AnalyteResultType.NuclearExpressionStatus,
};

@Component({
    selector: 'tumor-marker-form',
    templateUrl: './tumor-marker-form.component.html',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        RadioButton,
        SelectButton,
        Tooltip,
        ButtonModule,
        RadioSelectComponent,
        MeasureInputComponent,
        MultiReferenceSelectComponent,
        FormControlErrorComponent,
    ]
})
export class TumorMarkerFormComponent extends AbstractFormBase {

  // Input signal for initial data passed to the form
  initialData = input<TumorMarker>();

  // Service injections
  readonly #tumorMarkersService: TumorMarkersService = inject(TumorMarkersService);
  readonly #neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService);
  readonly #terminologyService: TerminologyService = inject(TerminologyService);
  readonly #fb = inject(FormBuilder);

  // Create and update service methods for the form data
  public readonly createService = (payload: TumorMarkerCreate) => this.#tumorMarkersService.createTumorMarker({tumorMarkerCreate: payload})
  public readonly updateService = (id: string, payload: TumorMarkerCreate) => this.#tumorMarkersService.updateTumorMarkerById({tumorMarkerId: id, tumorMarkerCreate: payload})


  // Define the form
  public form = this.#fb.group({
    date: this.#fb.control<string | null>(null, Validators.required),
    stagedEntities: this.#fb.control<string[]>([], Validators.required),
    analyte: this.#fb.control<CodedConcept | null>(null, Validators.required),
    valueType: this.#fb.control<string | null>('', Validators.required),
    massConcentration: this.#fb.control<Measure | null>(null),
    substanceConcentration: this.#fb.control<Measure | null>(null),
    arbitraryConcentration: this.#fb.control<Measure | null>(null),
    fraction: this.#fb.control<Measure | null>(null),
    immunoHistoChemicalScore: this.#fb.control<TumorMarkerImmunohistochemicalScoreChoices | null>(null),
    presence: this.#fb.control<TumorMarkerPresenceChoices | null>(null),
    nuclearExpressionStatus: this.#fb.control<TumorMarkerNuclearExpressionStatusChoices | null>(null),
    immuneCellScore: this.#fb.control<TumorMarkerImmuneCellScoreChoices | null>(null),
    tumorProportionScore: this.#fb.control<TumorMarkerTumorProportionScoreChoices | null>(null),
    combinedPositiveScore: this.#fb.control<Measure | null>(null),
  });
  
  // Effect to update the form when the initial data passed
  readonly #onInitialDataChangeEffect = effect((): void => {
    const data = this.initialData();
    if (!data) return;  
    this.form.patchValue({
      date: data.date ?? null,
      stagedEntities: data.relatedEntitiesIds ?? [],
      analyte: data.analyte ?? null,
      massConcentration: data.massConcentration ?? null,
      substanceConcentration: data.substanceConcentration ?? null,
      arbitraryConcentration: data.arbitraryConcentration ?? null,
      fraction: data.fraction ?? null,
      immunoHistoChemicalScore: data.immunohistochemicalScore ?? null,
      presence: data.presence ?? null,
      nuclearExpressionStatus: data.nuclearExpressionStatus ?? null,
      immuneCellScore: data.immuneCellScore ?? null,
      tumorProportionScore: data.tumorProportionScore ?? null,
      combinedPositiveScore: data.combinedPositiveScore ?? null,
      valueType: this.initialData() ? Object.entries(valueTypeMap).filter(([key, value]) => (this.initialData() as TumorMarker)[key as keyof TumorMarker]).map(([key, value]) => value)[0] : null,
    });
  });

  // API Payload construction function
  readonly payload = (): TumorMarkerCreate => {    
    const data = this.form.value;
    return {
      caseId: this.caseId(),
      relatedEntitiesIds: data.stagedEntities!,
      date: data.date!,
      analyte: data.analyte!,
      massConcentration: data.valueType==AnalyteResultType.MassConcentration ? data.massConcentration! : undefined,
      substanceConcentration: data.valueType==AnalyteResultType.SubstanceConcentration ? data.substanceConcentration! : undefined,
      arbitraryConcentration: data.valueType==AnalyteResultType.ArbitraryConcentration ? data.arbitraryConcentration! : undefined,
      fraction: data.valueType==AnalyteResultType.Fraction ? data.fraction! : undefined,
      immunohistochemicalScore: data.valueType==AnalyteResultType.ImmunoHistoChemicalScore ? data.immunoHistoChemicalScore! : undefined,
      presence: data.valueType==AnalyteResultType.Presence ? data.presence! : undefined,
      nuclearExpressionStatus: data.valueType==AnalyteResultType.NuclearExpressionStatus ? data.nuclearExpressionStatus! : undefined,
      immuneCellScore: data.valueType==AnalyteResultType.ImmuneCellsScore ? data.immuneCellScore! : undefined,
      tumorProportionScore: data.valueType==AnalyteResultType.TumorProportionScore ? data.tumorProportionScore! : undefined,
      combinedPositiveScore: data.valueType==AnalyteResultType.CombinedPositiveScore ? data.combinedPositiveScore! : undefined,
    };
  }

  // All analytes supported by the platform
  public analytes = rxResource({
    request: () => ({terminologyName: 'TumorMarkerAnalyte', limit: 50}),
    loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(map(response => response.items)),
  }) 

  // All neoplastic entities related to this patient case
  public relatedEntities = rxResource({
    request: () => ({caseId: this.caseId()}),
    loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
  }) 

  // Human readable choices for UI elements
  public readonly analyteResultTypes = AnalyteResultType;
  public readonly analyteResultTypeChoices: RadioChoice[] = [
    { name: 'Mass Concentration', value: AnalyteResultType.MassConcentration }, 
    { name: 'Substance Concentration', value: AnalyteResultType.SubstanceConcentration }, 
    { name: 'Arbitrary Concentration', value: AnalyteResultType.ArbitraryConcentration }, 
    { name: 'Fraction', value: AnalyteResultType.Fraction }, 
    { name: 'Immunohistochemical Score', value: AnalyteResultType.ImmunoHistoChemicalScore }, 
    { name: 'Presence', value: AnalyteResultType.Presence }, 
    { name: 'Nuclear Expression Status', value: AnalyteResultType.NuclearExpressionStatus }, 
    { name: 'Immune Cells Score', value: AnalyteResultType.ImmuneCellsScore }, 
    { name: 'Tumor Proportion Score', value: AnalyteResultType.TumorProportionScore }, 
    { name: 'Combined Positive Score', value: AnalyteResultType.CombinedPositiveScore },
  ]
  public readonly tumorMarkerPresenceChoices: RadioChoice[] = [
    { name: 'Positive', value: TumorMarkerPresenceChoices.Positive },
    { name: 'Negative', value: TumorMarkerPresenceChoices.Negative },
    { name: 'Indeterminate', value: TumorMarkerPresenceChoices.Indeterminate,
    },
  ]
  public readonly tumorMarkerNuclearExpressionStatusChoices: RadioChoice[] = [
    { name: 'Intact', value: TumorMarkerNuclearExpressionStatusChoices.Intact },
    { name: 'Loss', value: TumorMarkerNuclearExpressionStatusChoices.Loss },
    { name: 'Indeterminate', value: TumorMarkerNuclearExpressionStatusChoices.Indeterminate }
  ]
  public readonly tumorMarkerImmunohistochemicalScoreChoices: RadioChoice[] = [
    { name: '0', value: TumorMarkerImmunohistochemicalScoreChoices._0 },
    { name: '1+', value: TumorMarkerImmunohistochemicalScoreChoices._1 },
    { name: '2+', value: TumorMarkerImmunohistochemicalScoreChoices._2 },
    { name: '3+', value: TumorMarkerImmunohistochemicalScoreChoices._3 },
    { name: 'Indeterminate', value: TumorMarkerImmunohistochemicalScoreChoices.Indeterminate }
  ]
  public readonly tumorMarkerImmuneCellScoreChoices: RadioChoice[] = [
    { name: 'IC0', value: TumorMarkerImmuneCellScoreChoices.Ic0 },
    { name: 'IC1', value: TumorMarkerImmuneCellScoreChoices.Ic1 },
    { name: 'IC2', value: TumorMarkerImmuneCellScoreChoices.Ic2 },
    { name: 'IC3', value: TumorMarkerImmuneCellScoreChoices.Ic3 }
  ]
  public readonly tumorMarkerTumorProportionScoreChoices: RadioChoice[] = [
    { name: 'TC0', value: TumorMarkerTumorProportionScoreChoices.Tc0 },
    { name: 'TC1', value: TumorMarkerTumorProportionScoreChoices.Tc1 },
    { name: 'TC2', value: TumorMarkerTumorProportionScoreChoices.Tc2 },
    { name: 'TC3', value: TumorMarkerTumorProportionScoreChoices.Tc3 }
  ]

  public allowedResultTypes = signal([] as string[]);
  
  #currentAnalyte = toSignal(this.form.controls['analyte'].valueChanges);
  #currentValueType = toSignal(this.form.controls['valueType'].valueChanges);
  #onValueTypeChangeEffect = effect(() => this.updateValidators(this.#currentValueType()))
  #onAnalyteChangeEffect = effect(() => {
    this.allowedResultTypes.set(this.#currentAnalyte()? this.#currentAnalyte()!.properties!['valueTypes'] : []);    
  })
  #setSingleValueTypeEffect = effect(() => {
    if (this.allowedResultTypes().length == 1){
      this.form.get('valueType')?.setValue(this.allowedResultTypes()[0])
    } else if (!this.allowedResultTypes().includes(this.form.get('valueType')?.value || '')) {
      this.form.get('valueType')?.setValue(null)
    }
  })

  private updateValidators(valueType: string | null | undefined): void {
    if (!valueType) {
      return;
    }
    const massConcentrationControl = this.form.get('massConcentration');
    const arbitraryConcentrationControl = this.form.get('arbitraryConcentration');
    const substanceConcentrationControl = this.form.get('substanceConcentration');
    const fractionControl = this.form.get('fraction');
    const presenceControl = this.form.get('presence');
    const immunoHistoChemicalScoreControl = this.form.get('immunoHistoChemicalScore');
    const nuclearExpressionStatusControl = this.form.get('nuclearExpressionStatus');
    const immuneCellScoreControl = this.form.get('immuneCellScore');
    const tumorProportionScoreControl = this.form.get('tumorProportionScore');
    const combinedPositiveScoreControl = this.form.get('combinedPositiveScore');

    const controls = [
      massConcentrationControl, arbitraryConcentrationControl, substanceConcentrationControl, fractionControl,
      presenceControl, immunoHistoChemicalScoreControl, nuclearExpressionStatusControl,
      tumorProportionScoreControl, tumorProportionScoreControl, combinedPositiveScoreControl
    ]
    
    controls.forEach(control => {
      control?.removeValidators(Validators.required);
    });

    switch (valueType) {
      case AnalyteResultType.MassConcentration:
        massConcentrationControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.ArbitraryConcentration:
        arbitraryConcentrationControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.SubstanceConcentration:
        substanceConcentrationControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.Fraction:
        fractionControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.Presence:
        presenceControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.ImmunoHistoChemicalScore:
        immunoHistoChemicalScoreControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.NuclearExpressionStatus:
        nuclearExpressionStatusControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.ImmuneCellsScore:
        immuneCellScoreControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.TumorProportionScore:
        tumorProportionScoreControl?.addValidators(Validators.required);
        break;
      case AnalyteResultType.CombinedPositiveScore:
        combinedPositiveScoreControl?.addValidators(Validators.required);
        break;
    }
    controls.forEach(control => {
      control?.updateValueAndValidity();
    });
  };

}