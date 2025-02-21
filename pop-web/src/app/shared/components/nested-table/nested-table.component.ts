import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { TableModule } from 'primeng/table';

@Component({
  standalone: true,
  selector: 'pop-nested-table',
  templateUrl: './nested-table.component.html',
  imports: [
    TableModule, CommonModule
  ]
})
export class NestedTableComponent {
  @Input() nestedData: any;

  getColumns(data: any[]): string[] {
    const allKeys = new Set<string>();
    console.log(data)
    data.forEach(item => Object.keys(item).forEach(key => allKeys.add(key)));
    return Array.from(allKeys);
  }

  isNested(value: any): boolean {
    return typeof value === 'object' && value !== null;
  }
}
