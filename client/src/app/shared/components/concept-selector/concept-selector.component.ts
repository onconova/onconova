import { Component, Input, forwardRef, inject, OnInit, OnChanges, SimpleChanges, input, computed, signal, effect, output } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Observable, catchError, first, map, of } from 'rxjs';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { RadioButton } from 'primeng/radiobutton';
import { SelectButton } from 'primeng/selectbutton';
import { ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';

import { TerminologyService, CodedConcept, PaginatedCodedConcept } from 'onconova-api-client';
import { rxResource } from '@angular/core/rxjs-interop';
import { Skeleton } from "primeng/skeleton";

@Component({
    selector: 'onconova-concept-selector',
    templateUrl: './concept-selector.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => ConceptSelectorComponent),
            multi: true,
        },
    ],
    imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AutoCompleteModule,
    RadioButton,
    Skeleton,
    SelectButton,
    Skeleton
]
})
export class ConceptSelectorComponent implements ControlValueAccessor {

    terminology = input.required<string>();
    showSynonyms = input<boolean>(true);
    showCodes = input<boolean>(false);
    multiple = input<boolean>(false);
    disabled = input<boolean>(false);
    placeholder = input<string>('Select or search an option');
    conceptsLimit = input<number>(50);
    widget = input<'autocomplete' | 'radio' | 'selectbutton'>('autocomplete');
    returnCode = input<boolean>(false);
    selected = output<CodedConcept>();
    suggestions: CodedConcept[] = [];
    readonly #terminologyService = inject(TerminologyService);
    readonly #messageService = inject(MessageService);

    public formControl: FormControl = new FormControl();
    
    public query = signal<string>('');
    
    public terminologySize = rxResource({
        request: () => ({terminologyName: this.terminology()}),
        loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(
            map((response) => response.count)
        )   
    })
    public subsetSize = computed( () => this.concepts.value()?.length || 0);
    public concepts = rxResource({
        request: () => ({terminologyName: this.terminology(), query: this.query(), limit: this.conceptsLimit()}),
        loader: ({request}) => this.#terminologyService.getTerminologyConcepts(request).pipe(                   
            catchError(error => {
                console.error('Error loading terminology concepts:', error);
                this.#messageService.add({ severity: 'error', summary: 'Error', detail: 'Error loading terminology concepts:' + error});
                return of({items:[], count: 0} as PaginatedCodedConcept); // Return empty array as fallback
            }),
            map((response: PaginatedCodedConcept) => {
                this.terminologySize.set(response.count);
                this.suggestions = response.items;
                return response.items
            }
        )), 
    }) 



    writeValue(value: any): void {
        if (this.returnCode()) {
            if (value) {
                // Find the concept by code
                this.#terminologyService.getTerminologyConcepts({terminologyName: this.terminology(), codes: this.multiple() ? value : [value]}).pipe(first()).subscribe({
                    next: (response) => {
                        if (this.multiple()) {
                            value = value.map((val: string) => response.items.find(c => c.code === val));
                        } else {
                            value = response.items.find(c => c.code === value);
                        }
                        this.formControl.patchValue(value);
                    }
                })
            }
        } 
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => {
            if (this.returnCode()) {
                if (this.multiple()) {
                    fn(val ? val.map((c: CodedConcept) => c.code) : []);
                } else {
                    fn(val ? val.code : null);
                }
            } else {
                fn(val);
            }
            this.selected.emit(val)
        });
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}