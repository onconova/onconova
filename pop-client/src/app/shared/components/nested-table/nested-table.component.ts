import { CommonModule } from '@angular/common';
import { Component, inject, Input } from '@angular/core';

import { TableModule } from 'primeng/table';
import { Button } from 'primeng/button';
import { CamelCaseToTitleCasePipe } from "src/app/shared/pipes/camel-to-title-case.pipe";
import { TypeCheckService } from '../../services/type-check.service';

@Component({
    selector: 'pop-nested-table',
    templateUrl: './nested-table.component.html',
    imports: [
        TableModule, CommonModule, Button, CamelCaseToTitleCasePipe
    ]
})
export class NestedTableComponent {

  private typeCheckService = inject(TypeCheckService); 
  public isArray = this.typeCheckService.isArray;

  @Input() nestedData!: any[];
  public nestedDataColumn!: any[];

  ngOnInit() {
    this.nestedDataColumn = this.getColumns(this.nestedData);
  }

  getColumns(data: any[]): string[] {
    const allKeys = new Set<string>();
    data.forEach(item => Object.keys(item).forEach(key => allKeys.add(key)));
    return Array.from(allKeys);
  }

  isNested(value: any): boolean {
    return value !== null && typeof value === 'object' && typeof value[0] === 'object';
  }
}
