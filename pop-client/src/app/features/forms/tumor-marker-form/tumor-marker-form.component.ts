import { Component, inject, OnInit,ViewEncapsulation } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable,map } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { TestTubeDiagonal } from 'lucide-angular';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { SelectButton } from 'primeng/selectbutton';
import { Tooltip } from 'primeng/tooltip';
import { RadioButton } from 'primeng/radiobutton';

import { 
  NeoplasticEntity, 
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
} from '../../../shared/openapi'

import { 
  DatePickerComponent,
  FormControlErrorComponent ,
  MeasureInputComponent,
  MultiReferenceSelectComponent,
  RadioSelectComponent, 
  RadioChoice
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';

@Component({
    selector: 'tumor-marker-form',
    styleUrl: './tumor-marker-form.component.css',
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
export class TumorMarkerFormComponent extends AbstractFormBase implements OnInit {

  private readonly tumorMarkersService: TumorMarkersService = inject(TumorMarkersService)
  private readonly neoplasticEntitiesService: NeoplasticEntitiesService = inject(NeoplasticEntitiesService)
  private readonly terminologyService: TerminologyService = inject(TerminologyService)
  public readonly formBuilder = inject(FormBuilder)

  public readonly createService = (payload: TumorMarkerCreate) => this.tumorMarkersService.createTumorMarker({tumorMarkerCreate: payload})
  public readonly updateService = (id: string, payload: TumorMarkerCreate) => this.tumorMarkersService.updateTumorMarkerById({tumorMarkerId: id, tumorMarkerCreate: payload})

  public readonly title: string = 'Tumor Marker'
  public readonly subtitle: string = 'Add new tumor marker'
  public readonly icon = TestTubeDiagonal;

  public readonly analyteResultTypes = AnalyteResultType;
  public readonly analytes$: Observable<CodedConcept[]> = this.terminologyService.getTerminologyConcepts({terminologyName: 'TumorMarkerAnalyte'}).pipe(
    map((data) => data.items || [])
  );
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

  private caseId!: string;
  public initialData: TumorMarkerCreate | any = {};
  public relatedEntities: NeoplasticEntity[] = []; 
  public resultsType: string[] = [];


  ngOnInit() {
    // Construct the form 
    this.constructForm()
    // Fetch any primary neoplastic entities that could be related to a new entry 
    this.getRelatedEntities()

    this.form.get('valueType')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(valueType => {
      this.onValueTypeChange(valueType);
    })
    this.form.get('analyte')?.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(analyte => {
      this.onAnalyteChange(analyte)
    })
    this.onAnalyteChange(this.form.get('analyte')?.value)
    if (this.form.get('immuneCellScore')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.ImmuneCellsScore)
    } else if (this.form.get('tumorProportionScore')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.TumorProportionScore)
    } else if (this.form.get('combinedPositiveScore')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.CombinedPositiveScore)
    } else if (this.form.get('massConcentration')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.MassConcentration)
    } else if (this.form.get('substanceConcentration')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.SubstanceConcentration)
    } else if (this.form.get('arbitraryConcentration')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.ArbitraryConcentration)
    } else if (this.form.get('fraction')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.Fraction)
    } else if (this.form.get('immunoHistoChemicalScore')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.ImmunoHistoChemicalScore)
    } else if (this.form.get('presence')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.Presence)
    } else if (this.form.get('nuclearExpressionStatus')?.value) {
      this.form.get('valueType')?.setValue(AnalyteResultType.NuclearExpressionStatus)
    } 
    this.onValueTypeChange(this.form.get('valueType')?.value);

  }

  constructForm(): void {
    this.form = this.formBuilder.group({
        date: [this.initialData?.date, Validators.required],
        stagedEntities: [this.initialData?.relatedEntitiesIds, Validators.required],
        analyte: [this.initialData?.analyte,Validators.required],
        valueType: ['',Validators.required],
        massConcentration: [this.initialData?.massConcentration],
        substanceConcentration: [this.initialData?.substanceConcentration],
        arbitraryConcentration: [this.initialData?.arbitraryConcentration],
        fraction: [this.initialData?.fraction],
        immunoHistoChemicalScore: [this.initialData?.immunoHistoChemicalScore],
        presence: [this.initialData?.presence],
        nuclearExpressionStatus: [this.initialData?.nuclearExpressionStatus],
        immuneCellScore: [this.initialData?.immuneCellScore],
        tumorProportionScore: [this.initialData?.tumorProportionScore],
        combinedPositiveScore: [this.initialData?.combinedPositiveScore],
    });
  }
  

  constructAPIPayload(data: any): TumorMarkerCreate {    
    return {
      caseId: this.caseId,
      relatedEntitiesIds: data.stagedEntities,
      date: data.date,
      analyte: data.analyte,
      massConcentration: data.valueType==AnalyteResultType.MassConcentration ? data.massConcentration : null,
      substanceConcentration: data.valueType==AnalyteResultType.SubstanceConcentration ? data.substanceConcentration : null,
      arbitraryConcentration: data.valueType==AnalyteResultType.ArbitraryConcentration ? data.arbitraryConcentration : null,
      fraction: data.valueType==AnalyteResultType.Fraction ? data.fraction : null,
      immunohistochemicalScore: data.valueType==AnalyteResultType.ImmunoHistoChemicalScore ? data.immunohistochemicalScore : null,
      presence: data.valueType==AnalyteResultType.Presence ? data.presence : null,
      nuclearExpressionStatus: data.valueType==AnalyteResultType.NuclearExpressionStatus ? data.nuclearExpressionStatus : null,
      immuneCellScore: data.valueType==AnalyteResultType.ImmuneCellsScore ? data.immuneCellScore : null,
      tumorProportionScore: data.valueType==AnalyteResultType.TumorProportionScore ? data.tumorProportionScore : null,
      combinedPositiveScore: data.valueType==AnalyteResultType.CombinedPositiveScore ? data.combinedPositiveScore : null,
    };
  }

  private getRelatedEntities(): void {
    this.neoplasticEntitiesService.getNeoplasticEntities({caseId:this.caseId})
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(
      (response) => {
          this.relatedEntities = response.items
      }
    )
  }

  private onAnalyteChange(analyte: any) {
    {
      if (analyte) {
        this.resultsType = analyte.properties.valueTypes;
        if (this.resultsType.length == 1){
          this.form.get('valueType')?.setValue(this.resultsType[0])
        } else {
          this.form.get('valueType')?.setValue(null)
        }
      } else {
        this.resultsType = []
      }
    }
  }

  private onValueTypeChange(valueType: string): void {
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