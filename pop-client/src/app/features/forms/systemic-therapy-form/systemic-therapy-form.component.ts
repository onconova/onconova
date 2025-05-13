import { Component, computed, effect, inject, input} from '@angular/core';
import { FormBuilder, Validators, FormsModule, ReactiveFormsModule, FormArray, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';

import { ButtonModule } from 'primeng/button';
import { Fluid } from 'primeng/fluid';
import { InputNumber } from 'primeng/inputnumber';
import { Fieldset } from 'primeng/fieldset';

import { 
    CodedConcept,
    NeoplasticEntitiesService, 
    SystemicTherapyCreate,
    SystemicTherapyMedication,
    SystemicTherapyMedicationCreate,
    SystemicTherapiesService,
    SystemicTherapy,
    SystemicTherapyIntentChoices,
    Period,
    Measure
} from '../../../shared/openapi'

import { 
  ConceptSelectorComponent, 
  DatePickerComponent,
  FormControlErrorComponent ,
  MultiReferenceSelectComponent,
  RadioChoice,
  RadioSelectComponent,
  MeasureInputComponent,
} from '../../../shared/components';

import { AbstractFormBase } from '../abstract-form-base.component';
import { map } from 'rxjs';

@Component({
    selector: 'systemic-therapy-form',
    templateUrl: './systemic-therapy-form.component.html',
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        DatePickerComponent,
        Fluid,
        InputNumber,
        ButtonModule,
        Fieldset,
        MeasureInputComponent,
        ConceptSelectorComponent,
        MultiReferenceSelectComponent,
        RadioSelectComponent,
        FormControlErrorComponent,
    ]
})
export class SystemicTherapyFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<SystemicTherapy>();

    // Service injections
    readonly #systemicTherapiesService = inject(SystemicTherapiesService);
    readonly #neoplasticEntitiesService = inject(NeoplasticEntitiesService);
    readonly #fb = inject(FormBuilder);

  // Create and update service methods for the form data
    public readonly createService = (payload: SystemicTherapyCreate) => this.#systemicTherapiesService.createSystemicTherapy({systemicTherapyCreate: payload});
    public readonly updateService = (id: string, payload: SystemicTherapyCreate) => this.#systemicTherapiesService.updateSystemicTherapy({systemicTherapyId: id, systemicTherapyCreate: payload})
    override readonly subformsServices = [{
        payloads: this.constructMedicationPayloads.bind(this),
        deletedEntries: this.getDeletedMedications.bind(this),
        delete: (parentId: string, id: string) => this.#systemicTherapiesService.deleteSystemicTherapyMedication({systemicTherapyId: parentId, medicationId: id}),
        create: (parentId: string, payload: SystemicTherapyMedicationCreate) => this.#systemicTherapiesService.createSystemicTherapyMedication({systemicTherapyId: parentId, systemicTherapyMedicationCreate: payload}),
        update: (parentId: string, id: string, payload: SystemicTherapyMedicationCreate) => this.#systemicTherapiesService.updateSystemicTherapyMedication({systemicTherapyId: parentId, medicationId: id, systemicTherapyMedicationCreate: payload}),
    }]
    #deletedMedications: string[] = [];

    // Define the main form
    public form = this.#fb.group({
        period: this.#fb.control<Period | string | null>(null, Validators.required),
        targetedEntities: this.#fb.control<string[] | null>(null, Validators.required),
        drugs: this.#fb.nonNullable.control<CodedConcept[]>([], Validators.required),
        cycles: this.#fb.control<number | null>(null, Validators.required),
        intent: this.#fb.control<SystemicTherapyIntentChoices | null>(null, Validators.required),
        isAdjunctive: this.#fb.control<boolean>(false, Validators.required),
        adjunctiveRole: this.#fb.control<CodedConcept | null>(null),
        terminationReason: this.#fb.control<CodedConcept | null>(null),
        medications: this.#fb.array<FormGroup>([]),
      });

    readonly #onInitialDataChangeEffect = effect((): void => {
            const data = this.initialData();
            if (!data) return;
            
            this.form.patchValue({
                period: data.period ?? null,
                targetedEntities: data.targetedEntitiesIds ?? null,
                drugs: data.medications?.map((med: any) => med.drug) ?? [],
                cycles: data.cycles ?? null,
                intent: data.intent ?? null,
                isAdjunctive: data.adjunctiveRole ? true : false,
                adjunctiveRole: data.adjunctiveRole ?? null,
                terminationReason: data.terminationReason ?? null,
        });
        (data.medications ?? []).forEach((initialData: SystemicTherapyMedication) => {
            this.form.controls.medications.push(this.#medicationForm(initialData));
        });
    });

    //Definition for the dynamic subform constructor
    #medicationForm = (initialData: SystemicTherapyMedication) => this.#fb.group({
        id: this.#fb.control<string | null>(
            initialData.id || null
        ),
        drug: this.#fb.control<CodedConcept | null>(
            initialData.drug || null, 
            Validators.required
        ),
        route: this.#fb.control<CodedConcept | null>(
            initialData.route || null
        ),
        dosageType: this.#fb.control<string | null>(
            this.getInitialDosageType(initialData)
        ),
        dosageMass: this.#fb.control<Measure | null>(
            initialData.dosageMass || null
        ),
        dosageMassConcentration: this.#fb.control<Measure | null>(
            initialData.dosageMassConcentration || null
        ),
        dosageVolume: this.#fb.control<Measure | null>(
            initialData.dosageVolume || null
        ),
        dosageMassSurface: this.#fb.control<Measure | null>(
            initialData.dosageRateMassSurface || null
        ),
        dosageRateMass: this.#fb.control<Measure | null>(
            initialData.dosageRateMass || null
        ),
        dosageRateMassConcentration: this.#fb.control<Measure | null>(
            initialData.dosageRateMassConcentration || null
        ),
        dosageRateVolume: this.#fb.control<Measure | null>(
            initialData.dosageRateVolume || null
        ),
        dosageRateMassSurface: this.#fb.control<Measure | null>(
            initialData.dosageRateMassSurface || null
        ),
    })



    // API Payload construction functions
    readonly payload = (): SystemicTherapyCreate => {    
        const data = this.form.value;
        return {
            caseId: this.caseId(),
            targetedEntitiesIds: data.targetedEntities!,
            period: {
                start: typeof data.period == 'string' ? data.period.split(' - ')[0] : data.period!.start,
                end: typeof data.period == 'string' ? data.period.split(' - ')[1] : data.period!.end,
            },
            adjunctiveRole: data.isAdjunctive ? data.adjunctiveRole : null,
            cycles: data.cycles!,
            intent: data.intent!,
            terminationReason: data.terminationReason,
        };
    }
    private constructMedicationPayloads(): SystemicTherapyMedicationCreate[] {
        const data = this.form.value;
        return data.medications!.map((subformData: any) => {return {
            id: subformData.id,
            drug: subformData.drug,
            route: subformData.route,
            dosageMass: subformData.dosageMass,
            dosageMassConcentration: subformData.dosageMassConcentration,
            dosageVolume: subformData.dosageVolume,
            dosageMassSurface: subformData.dosageRateMassSurface,
            dosageRateMass: subformData.dosageRateMass,
            dosageRateMassConcentration: subformData.dosageRateMassConcentration,
            dosageRateVolume: subformData.dosageRateVolume,
            dosageRateMassSurface: subformData.dosageRateMassSurface,
        }})
    }

    // All neoplastic entities related to this patient case
    public relatedEntities = rxResource({
        request: () => ({caseId: this.caseId()}),
        loader: ({request}) => this.#neoplasticEntitiesService.getNeoplasticEntities(request).pipe(map(response => response.items)),
    }) 

    // Human readable choices for UI elements
    public readonly intentChoices: RadioChoice[] = [
        {name: 'Curative', value: SystemicTherapyIntentChoices.Curative},
        {name: 'Palliative', value: SystemicTherapyIntentChoices.Palliative},
    ]
    public readonly roleChoices: RadioChoice[] = [
        {name: 'Primary', value: false},
        {name: 'Adjunctive', value: true},
    ]
    public readonly dosageTypeChoices: RadioChoice[] = [
        {name: 'Mass', value: 'Mass'},
        {name: 'Volume', value: 'Volume'},
        {name: 'Mass Concentration', value: 'MassConcentration'},
        {name: 'Mass per surface', value: 'MassPerSurface'},
    ]

    // Subform update effect
    #selectedDrugs = toSignal(this.form.controls['drugs']!.valueChanges, {initialValue: []});
    #updateDosagesFormArrayEffect = effect(() => {
        const medicationFormArray = this.form.controls['medications'] as FormArray;
        // Add subforms for new drugs
        this.#selectedDrugs()!.forEach((drug: CodedConcept) => {
            if (!medicationFormArray.value.map( (medication: SystemicTherapyMedication) => medication.drug ).includes(drug) ){
                medicationFormArray.push(this.#medicationForm({drug: drug} as SystemicTherapyMedication));    
            }
        });
        // Remove subforms for drugs that are no longer selected
        medicationFormArray.value.forEach((medication: SystemicTherapyMedication, index: number) => {
            if (!this.#selectedDrugs()!.includes(medication.drug)) {
                if (medication.id) {
                    this.#deletedMedications.push(medication.id);
                }
                medicationFormArray.removeAt(index);
            }
        })        
    })

    // Adjunctive role effect
    #isAdjunctive = toSignal(this.form.controls['isAdjunctive']!.valueChanges);
    #updateAdjunctiveRoleEffect = effect(() => {
        if (this.#isAdjunctive()) {
            this.form.get('adjunctiveRole')?.addValidators(Validators.required);
        } else {
            this.form.get('adjunctiveRole')?.removeValidators(Validators.required);
            this.form.get('adjunctiveRole')?.setValue(null)
        }
        this.form.get('adjunctiveRole')?.updateValueAndValidity();

    })

    getInitialDosageType(data: SystemicTherapyMedication) {
        if (data.dosageMass || data.dosageRateMass) {
            return 'Mass'
        } else if (data.dosageMassConcentration || data.dosageRateMassConcentration) {
            return 'MassConcentration'
        }  else if (data.dosageMassSurface || data.dosageRateMassSurface) {
            return 'MassPerSurface'
        }  else if (data.dosageVolume || data.dosageRateVolume) {
            return 'Volume'
        }
        return null
    }

    private getDeletedMedications(): string[] {
        return this.#deletedMedications;
    }

}