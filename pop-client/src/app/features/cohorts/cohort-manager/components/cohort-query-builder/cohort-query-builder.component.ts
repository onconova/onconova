import { ChangeDetectorRef, Component, ElementRef, HostBinding, Input, forwardRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, ValidationErrors, AbstractControl, NG_VALIDATORS, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';

import { TooltipModule } from 'primeng/tooltip';
import { Button } from 'primeng/button';
import { ButtonGroup } from 'primeng/buttongroup';
import { SelectButton } from 'primeng/selectbutton';
import { Select } from 'primeng/select';
import { MultiSelect } from 'primeng/multiselect';
import { InputNumber } from 'primeng/inputnumber';
import { InputText } from 'primeng/inputtext';
import { Avatar } from 'primeng/avatar';
import { Message } from 'primeng/message';

import OpenAPISpecification from "../../../../../../../openapi.json";
import { DataResource, CohortQueryFilter} from 'src/app/shared/openapi';
import { ConceptSelectorComponent, DatePickerComponent, RangeInputComponent, MeasureInputComponent } from '../../../../../shared/components';

import { Entity, EntityMap, Field, FieldMap, InputContext, Option, QueryBuilderConfig, Rule, RuleFilter, RuleSet} from "./cohort-query-builder.interfaces";
import { MapOperatorsPipe } from './query-builder-operators.pipe';

export const CONTROL_VALUE_ACCESSOR: any = {
  provide: NG_VALUE_ACCESSOR,
  useExisting: forwardRef(() => CohortQueryBuilderComponent),
  multi: true
};

export const VALIDATOR: any = {
  provide: NG_VALIDATORS,
  useExisting: forwardRef(() => CohortQueryBuilderComponent),
  multi: true
};


@Component({
    standalone: true,
    selector: 'pop-cohort-query-builder',
    templateUrl: './cohort-query-builder.component.html',
    providers: [CONTROL_VALUE_ACCESSOR, VALIDATOR],
    imports: [
        CommonModule,
        FormsModule,
        Button,
        ButtonGroup,
        SelectButton,
        InputNumber,
        InputText,
        Avatar,
        Select,
        MultiSelect,
        TooltipModule,
        RangeInputComponent,
        ConceptSelectorComponent,
        DatePickerComponent,
        MeasureInputComponent,
        MapOperatorsPipe,
        Message,
    ]
})
export class CohortQueryBuilderComponent implements ControlValueAccessor {

    @Input() allowRuleset = true;
    @Input() allowCollapse = false;
    @Input() allowEmptyDefault = false;
    @Input() emptyMessage = "A ruleset cannot be empty. Please add a rule or remove it all together.";
    @Input() parentValue?: RuleSet;
    @Input() parentChangeCallback!: () => void;
    @Input() parentTouchedCallback!: () => void;
    @Input() persistValueOnFieldChange = false;
    @Input() disabled: boolean = false;
    @Input() data: RuleSet = { condition: "and", rules: [] };


    @ViewChild("treeContainer", { static: true }) treeContainer!: ElementRef;

    private defaultPersistValueTypes: string[] = ["string", "number", "time", "date", "boolean"];
    private defaultEmptyList: any[] = [];
    private operatorsCache: { [key: string]: string[] } = {};
    private inputContextCache = new Map<RuleFilter, InputContext>();

        
    public filterFields: Field[] = [];

    @HostBinding("attr.query-builder-condition") get condition() {
        return this.data?.condition;
    }
    private changeDetectorRef = inject(ChangeDetectorRef);

    // For ControlValueAccessor interface
    public onChangeCallback!: () => void;
    public onTouchedCallback!: () => any;
        
    public operators = CohortQueryFilter 
    private dataResources = [
        DataResource.PatientCase, DataResource.NeoplasticEntity, DataResource.TnmStaging, DataResource.FigoStaging,
        DataResource.BinetStaging, DataResource.RaiStaging, DataResource.BreslowDepth, DataResource.ClarkStaging,
        DataResource.IssStaging, DataResource.RissStaging, DataResource.GleasonGrade, DataResource.InssStage,
        DataResource.InrgssStage, DataResource.WilmsStage, DataResource.RhabdomyosarcomaClinicalGroup, DataResource.LymphomaStaging,
        DataResource.TumorMarker, DataResource.RiskAssessment, DataResource.TreatmentResponse, DataResource.TherapyLine,
        DataResource.SystemicTherapy, DataResource.PerformanceStatus, DataResource.Surgery, DataResource.Radiotherapy,
        DataResource.Lifestyle, DataResource.ComorbiditiesAssessment,  DataResource.FamilyHistory, DataResource.MolecularTumorBoard,
        DataResource.UnspecifiedTumorBoard, DataResource.AdverseEvent, DataResource.Vitals, DataResource.GenomicVariant,
        DataResource.TumorMutationalBurden, DataResource.MicrosatelliteInstability, DataResource.LossOfHeterozygosity,
        DataResource.HomologousRecombinationDeficiency,  DataResource.TumorNeoantigenBurden, DataResource.AneuploidScore
    ];    

    public fields: Field[] = this.dataResources.flatMap(resource => this.getEntityFields(resource));
    public entities: Entity[] = this.dataResources.map(resource => ({value: resource, name: resource.replace(/([a-z])([A-Z])/g, '$1 $2')}));

    public config: QueryBuilderConfig = {
        allowEmptyRulesets: false,
        entities: this.entities.reduce(
            (entityMap: any, entity: Entity) => {
                entityMap[entity.value as string] = entity
                return entityMap
            }, {} as EntityMap
        ),
        fields: this.fields.reduce(
            (fieldsMap: any, field: Field) => {                
                fieldsMap[field.value as string] = field
                return fieldsMap
            }, {} as FieldMap
        ),
    } 

    getEntityFields(entity: DataResource): Field[] {
        const ignoredFields: string[] = ['description', 'caseId', 'id','createdAt','updatedAt', 'createdBy', 'updatedBy', 'externalSourceId']
        // Get the schema definition of the entity from the OpenAPISpecification object
        const schemas = OpenAPISpecification.components.schemas
        // Get a list of all fields/properties in that schema
        const properties = schemas[entity].properties || {};
        // Iterate over each property
        return Object.entries(properties).filter(
            ([propertyKey,_]) => !ignoredFields.includes(propertyKey)
        ).flatMap(
            ([propertyKey,property]): Field | Field[] => {
                let title: string = property.title; 
                let description: string = property.description; 
                let extras: {[key: string]: string} = {};
                if (property.hasOwnProperty('x-terminology')) {
                    extras['terminology'] = property['x-terminology'];
                }
                
                let isArray: boolean = false;
                const nullable = property.anyOf && property.anyOf[property.anyOf.length-1].type === 'null'
                if (nullable) {
                    property = property.anyOf[0];
                } 
                if (property.items) {
                    property = property.items;                    
                    isArray = true;
                }
                let propertyType: string;
                if (property.type === undefined && property.$ref) {
                    propertyType = property.$ref.split('/').pop();
                } else {
                    propertyType = property.type;
                }        
                
                // Handle nested resources
                if ([
                    DataResource.SystemicTherapyMedication,
                    DataResource.RadiotherapyDosage,
                    DataResource.RadiotherapySetting,
                    DataResource.AdverseEventMitigation,
                    DataResource.AdverseEventSuspectedCause,
                    DataResource.MolecularTherapeuticRecommendation,

                ].includes(propertyType as DataResource)) {
                    return this.getEntityFields(propertyType as DataResource).map((nested_field: Field) => ({
                        name: `${property.title} - ${nested_field.name}`,
                        entity: entity,
                        value: `${entity}.${propertyKey}.${nested_field.value?.split('.').pop()}`,
                        options: nested_field.options,
                        type: nested_field.type,
                        operators: nested_field.operators,
                        description: nested_field.description,
                    }))
                }

                // Determine any selection options if the property has an enumeration
                // @ts-ignore
                let propertyEnum = property.enum || schemas[propertyType]?.enum;
                if (propertyEnum) {
                    extras['options'] = propertyEnum.map((option: any) => ({ value: option, label: option }));
                    propertyType = 'enum';
                }
                if (propertyType == 'string' && property.format) {
                    propertyType = property.format
                }
                if (propertyType == 'Measure') {
                    extras['measureType'] = property['x-measure'];
                    extras['defaultUnit'] = property['x-default-unit'];
                }
                propertyType = (isArray ? "Multi" : "") + propertyType;

                // Create a field object and add it to the array
                return {
                    name: title,
                    entity: entity,
                    value: `${entity}.${propertyKey}`,
                    type: propertyType,
                    operators: this.getTypeFilterOperators(propertyType),
                    description: description,
                    ...extras,
                }
        }) as Field[];
    }



  validate(control: AbstractControl): ValidationErrors | null {
    const errors: { [key: string]: any } = {};
    const ruleErrorStore = [] as any;
    let hasErrors = false;

    if (this.data.rules.length == 0) {
        return null
    }

    if (!this.config.allowEmptyRulesets && this.checkEmptyRuleInRuleset(this.data)) {
      errors['empty'] = "Empty rulesets are not allowed.";
      hasErrors = true;
    }

    this.validateRulesInRuleset(this.data, ruleErrorStore);

    if (ruleErrorStore.length) {
      errors['rules'] = ruleErrorStore;
      hasErrors = true;
    }
    return hasErrors ? errors : null;
  }

  @Input()
  get value(): RuleSet | null {
    if (this.data.rules.length) {
        let data =  {...this.data}
        data.rules = this.convertRule(data.rules, false) 
        return data        
    } else {
        return null
    }
  }
  set value(value: RuleSet | null) {
    
    if (value) {
        this.data = value;
    } else {
        if (this.allowEmptyDefault) {
            this.addRule()
        } else {
            this.data = {condition: 'and', rules: []}
        }
    }
    this.handleDataChange();
  }

  writeValue(obj: any): void {
    if (obj) {
        let data =  {...obj}
        data.rules = this.convertRule(data.rules, true) 
        this.value = data;
    } else {
        this.value = null
    }

  }
  registerOnChange(fn: any): void {
    this.onChangeCallback = () => fn(this.value);
  }
  registerOnTouched(fn: any): void {
    this.onTouchedCallback = () => fn(this.value);
  }


  private convertRule(rules: any, toInternal: boolean = true) {
    if (!rules || rules.length === 0) {
        return null
    }
    return rules.map((rule_: any) => {
        let rule = {...rule_};
        if (rule.filters && rule.filters.length > 0) {
            rule.filters = rule.filters.map((filter_: any) => {
                let filter = {...filter_}
                if (filter.field) {
                    if (toInternal) {
                        filter.field = `${rule.entity}.${filter.field}`
                    } else {
                        filter.field = filter.field.split('.').pop();
                    }
                }
                return filter
            })
        }
        // Recursively apply to nested rules
        if (rule.rules && rule.rules.length > 0) {
            rule.rules = this.convertRule(rule.rules, toInternal);
        }
        return rule
    });
  }

  getOperators(field: string): string[] {
    if (this.operatorsCache[field]) {
      return this.operatorsCache[field];
    }
    let operators = this.defaultEmptyList;
    const fieldObject = this.config.fields[field];

    if (this.config.getOperators) {
      return this.config.getOperators(field, fieldObject);
    }

    if (fieldObject && fieldObject.operators) {
      operators = fieldObject.operators;

    } else {
      console.warn(`No 'type' property found on field: '${field}'`);
    }

    // Cache reference to array object, so it won't be computed next time and trigger a rerender.
    this.operatorsCache[field] = operators;
    return operators;
  }

  getFields(entity: string): Field[] {
    if (this.entities?.length && entity) {
      return this.fields.filter((field) => {
        return field && field.entity === entity;
      });
    } else {
      return this.fields;
    }
  }

  getInputType(field: string, operator: string): string | null {
    if (this.config.getInputType) {
      return this.config.getInputType(field, operator);
    }

    if (!this.config.fields[field]) {
      throw new Error(
        `No configuration for field '${field}' could be found! Please add it to config.fields.`
      );
    }

    const type = this.config.fields[field].type;
    switch (operator) {
      case "is null":
      case "is not null":
        return null; // No displayed component
      case "in":
      case "not in":
        return type === "category" || type === "boolean" ? "multiselect" : type;
      default:
        return type;
    }
  }

  getOptions(field: string): Option[] {
    if (this.config.getOptions) {
      return this.config.getOptions(field);
    }
    return this.config.fields[field].options || this.defaultEmptyList;
  }


  getDefaultField(entity: Entity): Field | null {
    if (!entity) {
      return null;
    } else if (entity.defaultField !== undefined) {
      return this.getDefaultValue(entity.defaultField);
    } else {
      const entityFields = this.fields.filter((field) => {
        return field && field.entity === entity.value;
      });
      if (entityFields && entityFields.length) {
        return entityFields[0];
      } else {
        console.warn(
          `No fields found for entity '${entity.name}'. ` +
            `A 'defaultOperator' is also not specified on the field config. Operator value will default to null.`
        );
        return null;
      }
    }
  }

  getDefaultOperator(field: Field): string | null {
    if (field && field.defaultOperator !== undefined) {
      return this.getDefaultValue(field.defaultOperator);
    } else {
      const operators = this.getOperators(field.value as string);
      if (operators && operators.length) {
        return operators[0];
      } else {
        console.warn(
          `No operators found for field '${field.value}'. ` +
            `A 'defaultOperator' is also not specified on the field config. Operator value will default to null.`
        );
        return null;
      }
    }
  }

  addRule(parent?: RuleSet): void {
    if (this.disabled) {
      return;
    }

    parent = parent || this.data;
    if (this.config.addRule) {
      this.config.addRule(parent);
    } else {
      const field = this.fields[0];
      parent.condition = parent.condition || "and";
      parent.rules = parent.rules || [];
      let newRule: Rule = {
        filters: [],
        entity: field.entity
      };
      this.addRuleFilter(newRule)
      parent.rules = parent.rules.concat(newRule);
    }
    this.handleTouched();
    this.handleDataChange();
  }

  addRuleFilter(parent: Rule): void {
    if (this.disabled) {
      return;
    }
    
    if (this.config.addRuleFilter) {
      this.config.addRuleFilter(parent);
    } else {
      const entity: Entity = this.entities.find((e) => e.value === parent.entity) as Entity;
      const field = this.getDefaultField(entity) as Field;
      parent.filters = (parent.filters || []).concat([
        {
          field: field.value as string,
          operator: this.getDefaultOperator(field) as string,
          value: this.getDefaultValue(field.defaultValue),
        }
      ]);
    }

    this.handleTouched();
    this.handleDataChange();
  }


  removeRuleFilter(field: RuleFilter, parent: Rule): void {
    if (this.disabled) {
      return;
    }

    if (this.config.removeRuleFilter) {
      this.config.removeRuleFilter(field, parent);
    } else {
      parent.filters = parent.filters.filter((r) => r !== field);
    }
    this.handleTouched();
    this.handleDataChange();
  }

  removeRule(rule: Rule, parent?: RuleSet): void {
    if (this.disabled) {
      return;
    }

    parent = parent || this.data;
    if (this.config.removeRule) {
      this.config.removeRule(rule, parent);
    } else {
      parent.rules = parent.rules.filter((r) => r !== rule);
    }
    this.handleTouched(); 
    this.handleDataChange();
  }

  addRuleSet(parent?: RuleSet): void {
    if (this.disabled) {
      return;
    }

    parent = parent || this.data;
    if (this.config.addRuleSet) {
      this.config.addRuleSet(parent);
    } else {
      parent.rules = parent.rules.concat([{ condition: "and", rules: [] }]);
    }

    this.handleTouched();
    this.handleDataChange();
  }

  removeRuleSet(ruleset?: RuleSet, parent?: RuleSet): void {
    if (this.disabled) {
      return;
    }

    ruleset = ruleset || this.data;
    parent = parent || this.parentValue;
    if (this.config.removeRuleSet) {
      this.config.removeRuleSet(ruleset, parent);
    } else if (parent) {
      parent.rules = parent.rules.filter((r) => r !== ruleset);
    }

    this.handleTouched();
    this.handleDataChange();
  }

  transitionEnd(e: Event): void {
    this.treeContainer.nativeElement.style.maxHeight = null;
  }

  toggleCollapse(): void {
    this.computedTreeContainerHeight();
    setTimeout(() => {
      this.data.collapsed = !this.data.collapsed;
    }, 100);
  }

  computedTreeContainerHeight(): void {
    const nativeElement: HTMLElement = this.treeContainer.nativeElement;
    if (nativeElement && nativeElement.firstElementChild) {
      nativeElement.style.maxHeight = nativeElement.firstElementChild.clientHeight + 8 + "px";
    }
  }

  changeCondition(value: string): void {
    if (this.disabled) {
      return;
    }

    this.data.condition = value;
    this.handleTouched();
    this.handleDataChange();
  }

  changeOperator(filter: RuleFilter): void {
    if (this.disabled) {
      return;
    }

    if (this.config.coerceValueForOperator) {
      filter.value = this.config.coerceValueForOperator(filter.operator as string, filter.value, filter);
    } else {
      filter.value = this.coerceValueForOperator(filter.operator as string, filter.value, filter);
    }

    this.handleTouched();
    this.handleDataChange();
  }

  coerceValueForOperator(operator: string, value: any, filter: RuleFilter): any {
    const inputType: string | null = this.getInputType(filter.field, operator);
    if (inputType === "multiselect" && !Array.isArray(value)) {
      return [value];
    }
    return value;
  }

  changeInput(): void {
    if (this.disabled) {
      return;
    }

    this.handleTouched();
    this.handleDataChange();
  }

  changeField(fieldValue: string, filter: RuleFilter): void {
    if (this.disabled) {
      return;
    }

    const inputContext = this.inputContextCache.get(filter);
    const currentField = inputContext && inputContext.field;

    const nextField: Field = this.config.fields[fieldValue];

    const nextValue = this.calculateFieldChangeValue(currentField as Field, nextField, filter.value);

    if (nextValue !== undefined) {
      filter.value = nextValue;
    } else {
      delete filter.value;
    }

    filter.operator = this.getDefaultOperator(nextField) as string;

    // Create new context objects so templates will automatically update
    this.inputContextCache.delete(filter);
    this.handleTouched();
    this.handleDataChange();
  }

  changeEntity(entityValue: string, rule: Rule, index: number, data: RuleSet): void {
    if (this.disabled) {
      return;
    }
    let i = index;
    let rs = data;
    const entity: Entity = this.entities.find((e) => e.value === entityValue) as Entity;
    const defaultField: Field = this.getDefaultField(entity) as Field;
    if (!rs) {
      rs = this.data;
      i = rs.rules.findIndex((x) => x === rule);
    }
    rule.filters = [{
        field: defaultField.value as string,
    }];
    rs.rules[i] = rule;
    if (defaultField) {
      this.changeField(defaultField.value as string, rule.filters[0]);
    } else {
      this.handleTouched();
      this.handleDataChange();
    }
  }

  getDefaultValue(defaultValue: any): any {
    switch (typeof defaultValue) {
      case "function":
        return defaultValue();
      default:
        return defaultValue;
    }
  }

  private calculateFieldChangeValue(currentField: Field, nextField: Field, currentValue: any): any {
    if (this.config.calculateFieldChangeValue != null) {
      return this.config.calculateFieldChangeValue(currentField, nextField, currentValue);
    }

    const canKeepValue = () => {
      if (currentField == null || nextField == null) {
        return false;
      }
      return (
        currentField.type === nextField.type &&
        this.defaultPersistValueTypes.indexOf(currentField.type) !== -1
      );
    };

    if (this.persistValueOnFieldChange && canKeepValue()) {
      return currentValue;
    }

    if (nextField && nextField.defaultValue !== undefined) {
      return this.getDefaultValue(nextField.defaultValue);
    }

    return undefined;
  }

  private checkEmptyRuleInRuleset(ruleset: RuleSet): boolean {
    if (!ruleset || !ruleset.rules || ruleset.rules.length === 0) {
      return true;
    } else {
      return ruleset.rules.some((item: RuleSet | any) => {
        if (item.rules) {
          return this.checkEmptyRuleInRuleset(item);
        } else {
          return false;
        }
      });
    }
  }

  private validateRulesInRuleset(ruleset: RuleSet, errorStore: any[]) {
    if (ruleset && ruleset.rules && ruleset.rules.length > 0) {
      ruleset.rules.forEach((item) => {
        if ((item as RuleSet).rules) {
          return this.validateRulesInRuleset(item as RuleSet, errorStore);
        } else if ((item as Rule).filters) {
          item.filters.forEach(
            (filter: RuleFilter) => {
              if (!filter.operator || !filter.value) {
                errorStore.push(new Error());
              }
            }
          )
          const field = this.config.fields[(item as RuleFilter).field];
          if (field && field.validator) {
            const error = field.validator(item as Rule, ruleset);
            if (error != null) {
              errorStore.push(error);
            }
          }
        }
      });
    }
  }

  private handleDataChange(): void {
    this.changeDetectorRef.markForCheck();
    if (this.onChangeCallback) {
      this.onChangeCallback();
    }
    if (this.parentChangeCallback) {
      this.parentChangeCallback();
    }
  }

  private handleTouched(): void {
    if (this.onTouchedCallback) {
      this.onTouchedCallback();
    }
    if (this.parentTouchedCallback) {
      this.parentTouchedCallback();
    }
  }

    private getTypeFilterOperators(type: string): CohortQueryFilter[]  {
        switch (type) {
            case 'string':
                return [ 
                    CohortQueryFilter.ExactStringFilter,
                    CohortQueryFilter.NotExactStringFilter,
                    CohortQueryFilter.ContainsStringFilter, 
                    CohortQueryFilter.NotContainsStringFilter, 
                    CohortQueryFilter.BeginsWithStringFilter, 
                    CohortQueryFilter.NotBeginsWithStringFilter, 
                    CohortQueryFilter.EndsWithStringFilter, 
                    CohortQueryFilter.NotEndsWithStringFilter
                ]
            case 'Multistring':
                return [ 
                    CohortQueryFilter.ExactStringFilter,
                    CohortQueryFilter.NotExactStringFilter,
                    CohortQueryFilter.ContainsStringFilter, 
                    CohortQueryFilter.NotContainsStringFilter, 
                    CohortQueryFilter.BeginsWithStringFilter, 
                    CohortQueryFilter.NotBeginsWithStringFilter, 
                    CohortQueryFilter.EndsWithStringFilter, 
                    CohortQueryFilter.NotEndsWithStringFilter
                ]
            case 'boolean':
                return [ 
                    CohortQueryFilter.EqualsBooleanFilter,
                ]
            case 'enum':
                return [ 
                    CohortQueryFilter.EqualsEnumFilter,
                    CohortQueryFilter.NotEqualsEnumFilter,
                    CohortQueryFilter.AnyOfEnumFilter,
                    CohortQueryFilter.NotAnyOfEnumFilter,    
                ]
            case 'number':
                return [ 
                    CohortQueryFilter.EqualFloatFilter,
                    CohortQueryFilter.NotEqualFloatFilter,
                    CohortQueryFilter.LessThanFloatFilter,
                    CohortQueryFilter.LessThanOrEqualFloatFilter,
                    CohortQueryFilter.GreaterThanFloatFilter,
                    CohortQueryFilter.GreaterThanOrEqualFloatFilter,
                    CohortQueryFilter.BetweenFloatFilter,
                    CohortQueryFilter.NotBetweenFloatFilter
                ]
            case 'integer':
                return [ 
                    CohortQueryFilter.EqualIntegerFilter,
                    CohortQueryFilter.NotEqualIntegerFilter,
                    CohortQueryFilter.LessThanIntegerFilter,
                    CohortQueryFilter.LessThanOrEqualIntegerFilter,
                    CohortQueryFilter.GreaterThanIntegerFilter,
                    CohortQueryFilter.GreaterThanOrEqualIntegerFilter,
                    CohortQueryFilter.BetweenIntegerFilter,
                    CohortQueryFilter.NotBetweenIntegerFilter
                ]
            case 'date-time':
                return [ 
                    CohortQueryFilter.BeforeDateFilter,
                    CohortQueryFilter.AfterDateFilter,
                    CohortQueryFilter.OnOrBeforeDateFilter,
                    CohortQueryFilter.OnOrAfterDateFilter,
                    CohortQueryFilter.OnDateFilter,
                    CohortQueryFilter.NotOnDateFilter,
                ]
            case 'date':
                return [ 
                    CohortQueryFilter.BeforeDateFilter,
                    CohortQueryFilter.AfterDateFilter,
                    CohortQueryFilter.OnOrBeforeDateFilter,
                    CohortQueryFilter.OnOrAfterDateFilter,
                    CohortQueryFilter.OnDateFilter,
                    CohortQueryFilter.NotOnDateFilter,
                ]
            case 'Period':
                return [ 
                    CohortQueryFilter.OverlapsPeriodFilter,
                    CohortQueryFilter.NotOverlapsPeriodFilter,
                    CohortQueryFilter.ContainsPeriodFilter,
                    CohortQueryFilter.NotContainsPeriodFilter,
                    CohortQueryFilter.ContainedByPeriodFilter,
                    CohortQueryFilter.NotContainedByPeriodFilter
                ]
            case 'CodedConcept':
                return [ 
                    CohortQueryFilter.EqualsConceptFilter,
                    CohortQueryFilter.NotEqualsConceptFilter,
                    CohortQueryFilter.AnyOfConceptFilter,
                    CohortQueryFilter.NotAnyOfConceptFilter,
                    CohortQueryFilter.DescendantsOfConceptFilter
                ]
            case 'Measure':
                return [ 
                    CohortQueryFilter.EqualFloatFilter,
                    CohortQueryFilter.NotEqualFloatFilter,
                    CohortQueryFilter.LessThanFloatFilter,
                    CohortQueryFilter.LessThanOrEqualFloatFilter,
                    CohortQueryFilter.GreaterThanFloatFilter,
                    CohortQueryFilter.GreaterThanOrEqualFloatFilter,
                    CohortQueryFilter.BetweenFloatFilter,
                    CohortQueryFilter.NotBetweenFloatFilter
                ]
            case 'MultiCodedConcept':
                return [ 
                    CohortQueryFilter.AllOfConceptFilter,
                    CohortQueryFilter.NotAllOfConceptFilter,
                    CohortQueryFilter.NotEqualsConceptFilter,
                    CohortQueryFilter.AnyOfConceptFilter,
                    CohortQueryFilter.NotAnyOfConceptFilter,
                    CohortQueryFilter.DescendantsOfConceptFilter
                ]
            default:
                return []
        }
    }

}

