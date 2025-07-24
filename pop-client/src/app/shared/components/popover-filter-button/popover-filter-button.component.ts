import { CommonModule } from '@angular/common';
import { Component, contentChild, effect, forwardRef, inject, input, linkedSignal, signal, Signal, TemplateRef, ViewEncapsulation, WritableSignal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
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
        @if (internalValue()) {
            <p-buttongroup styleClass='selected-filter-button-group'>
                <p-button type="button" 
                    severity="secondary"
                    [label]="selectionLabelFcn()(internalValue())" 
                    (onClick)="popover.toggle($event)" 
                />
                <p-button styleClass='selected-filter-remove-button' icon="pi pi-times" severity="secondary" (onClick)="value().set(undefined)"/>
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
                    [ngTemplateOutletContext]="{ $implicit: internalValue }"
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
export class PopoverFilterButtonComponent {

    readonly label = input.required<string>()
    readonly selectionLabelFcn = input.required<CallableFunction>()
    readonly popoverContent = contentChild.required<TemplateRef<{$implicit: WritableSignal<any>}>>('popoverContent', { descendants: false });
    readonly value = input.required<WritableSignal<any>>()
    internalValue = linkedSignal<any>(() => this.value()())
    public formControl = new FormControl<any  | undefined>(undefined);

}