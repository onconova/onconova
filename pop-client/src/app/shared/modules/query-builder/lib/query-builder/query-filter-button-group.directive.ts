import { Directive, TemplateRef } from "@angular/core";

@Directive({ selector: "[queryRuleFilterButtonGroup]" })
export class QueryRuleFilterButtonGroupDirective {
  constructor(public template: TemplateRef<any>) {}
}
