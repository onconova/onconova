import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { InputNumberModule } from 'primeng/inputnumber';

@Component({
    standalone: true,
    imports: [FormsModule, InputNumberModule],
    selector: 'pop-range-input',
    template: `
        <div class="p-fluid p-grid"  style="align-items: center;">
        <div class="p-col">
            <span class="p-float-label">
            <p-inputnumber 
                [ngModel]="range[0]" 
                (ngModelChange)="updateRange(0, $event)"
                [disabled]="disabled"
                placeholder="Enter a value" 
                useGrouping="false" 
                mode="decimal" 
                [minFractionDigits]="1" 
                [maxFractionDigits]="3" 
                locale="en-US"/>
            </span>
        </div>
        <div>-</div>
        <div class="p-col">
            <span class="p-float-label">
            <p-inputnumber 
                [ngModel]="range[1]" 
                (ngModelChange)="updateRange(1, $event)"
                [disabled]="disabled"
                placeholder="Enter a value" 
                useGrouping="false" 
                mode="decimal" 
                [minFractionDigits]="1" 
                [maxFractionDigits]="3" 
                locale="en-US"/>
            </span>
        </div>
        </div>
    `,
    styles: [
        `
        .p-grid {
        display: flex;
        gap: 1rem;
        }
        `
    ]
})
export class RangeInputComponent {
  @Input() range !: number[];
  @Input() disabled: boolean = false;
  @Output() rangeChange = new EventEmitter<(number | null)[]>();

    ngOnInit() {
        this.range = this.range ?? [null, null] 
    }

  updateRange(index: number, value: number) {
    const newRange = [...this.range];
    newRange[index] = value;
    this.rangeChange.emit(newRange);
  }
}