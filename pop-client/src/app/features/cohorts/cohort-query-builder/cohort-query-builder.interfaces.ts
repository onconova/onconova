import { ValidationErrors } from "@angular/forms";

export interface RuleSet {
  condition: string;
  rules: Array<RuleSet | Rule | any>;
  collapsed?: boolean;
  isChild?: boolean;
}

export interface Rule {
  filters: RuleFilter[];
  entity?: string;
}

export interface RuleFilter {
  field: string;
  value?: any;
  operator?: string;
}

export interface Option {
  name: string;
  value: any;
}

export interface FieldMap {
  [key: string]: Field;
}

export interface Field {
  name: string;
  value?: string;
  description?: string;
  type: string;
  nullable?: boolean;
  options?: Option[];
  terminology?: string;
  measureType?: string;
  defaultUnit?: string;
  operators?: string[];
  defaultValue?: any;
  defaultOperator?: any;
  entity?: string;
  validator?: (rule: Rule, parent: RuleSet) => any | null;
}

export interface EntityMap {
  [key: string]: Entity;
}

export interface Entity {
  name: string;
  value?: string;
  defaultField?: any;
}

export interface QueryBuilderConfig {
  fields: FieldMap;
  entities?: EntityMap;
  allowEmptyRulesets?: boolean;
  getOperators?: (fieldName: string, field: Field) => string[];
  getInputType?: (field: string, operator: string) => string;
  getOptions?: (field: string) => Option[];
  addRuleSet?: (parent: RuleSet) => void;
  addRule?: (parent: RuleSet) => void;
  addRuleFilter?: (parent: Rule) => void;
  removeRuleSet?: (ruleset: RuleSet, parent?: RuleSet) => void;
  removeRule?: (rule: Rule, parent: RuleSet) => void;
  removeRuleFilter?: (field: RuleFilter, parent: Rule) => void;
  coerceValueForOperator?: (operator: string, value: any, ruleField: RuleFilter) => any;
  calculateFieldChangeValue?: (currentField: Field, nextField: Field, currentValue: any) => any;
}


export interface InputContext {
  onChange: () => void;
  getDisabledState: () => boolean;
  options: Option[];
  field: Field;
  $implicit: RuleFilter;
}
