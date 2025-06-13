import { CommonModule } from '@angular/common';
import { Component, contentChild, forwardRef, inject, input, Signal, TemplateRef, ViewEncapsulation } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Button } from 'primeng/button';
import { ButtonGroup } from 'primeng/buttongroup';
import { Popover } from 'primeng/popover';


@Component({
    selector: 'pop-popover-filter-button',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => PopoverFilterButtonComponent),
            multi: true,
        },
    ],
    template: `
        @if (formControl.value) {
            <p-buttongroup styleClass='selected-filter-button-group'>
                <p-button type="button" 
                    severity="secondary"
                    [label]="selectionLabelFcn()(formControl.value)" 
                    (onClick)="popover.toggle($event)" 
                />
                <p-button styleClass='selected-filter-remove-button' icon="pi pi-times" severity="secondary" (onClick)="formControl.setValue(undefined)"/>
            </p-buttongroup>
            } @else {
                <p-button type="button" 
                    styleClass='filter-add-button'
                    severity="secondary"
                    [outlined]="true"
                    icon="pi pi-filter" 
                    [label]="label()" 
                    (onClick)="popover.toggle($event)" 
                    [style]="{'border-style': 'dashed'}"
                />
            }
            <p-popover #popover>
                <ng-container 
                    [ngTemplateOutlet]="popoverContent()"
                    [ngTemplateOutletContext]="{formControl: formControl}"
                ></ng-container>    
            </p-popover>
    `,
    imports: [
        FormsModule,
        CommonModule,
        Button,
        ButtonGroup,
        Popover,

    ]
})
export class PopoverFilterButtonComponent implements ControlValueAccessor {

    readonly label = input.required<string>()
    readonly selectionLabelFcn = input.required<CallableFunction>()
    readonly popoverContent = contentChild.required<TemplateRef<any>>('popoverContent', { descendants: false });

  // Form control to track the value
  public formControl = new FormControl<any | undefined>(undefined);
    
  // Write value from the parent component into this component's form control
  writeValue(value: any): void {
    this.formControl.setValue(value);
  }

  // Register on change function to propagate changes to the parent form
  registerOnChange(fn: any): void {
    this.formControl.valueChanges.subscribe((val) => fn(val));
  }

  // Register on touched function to mark the form as touched when the user interacts with it
  registerOnTouched(fn: any): void {
    this.formControl.valueChanges.subscribe(val => fn(val));
  }

}