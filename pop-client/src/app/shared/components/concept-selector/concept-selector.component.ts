import { Component, Input, forwardRef, inject, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Observable, catchError, first, map, of } from 'rxjs';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { Button } from 'primeng/button';
import { RadioButton } from 'primeng/radiobutton';
import { ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';

import { TerminologyService } from '../../openapi/api/terminology.service';
import { CodedConcept, PaginatedCodedConcept } from '../../openapi';

@Component({
    standalone: true,
    selector: 'pop-concept-selector',
    styleUrl: './concept-selector.component.css',
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
        Button,
    ]
})
export class ConceptSelectorComponent implements ControlValueAccessor, OnInit, OnChanges {
    
    private readonly terminologyService: TerminologyService = inject(TerminologyService);
    private readonly messageService: MessageService = inject(MessageService);

    @Input({required: true}) terminology!: string;
    @Input() showSynonyms: boolean = true;
    @Input() showCodes: boolean = false;
    @Input() multiple: boolean = false;
    @Input() placeholder: string = 'Select or search an option';
    @Input() conceptsLimit: number = 100;
    @Input() widget: 'autocomplete' | 'radio' = 'autocomplete';
    @Input() returnCode: boolean = false;

    public formControl: FormControl = new FormControl();
    public concepts$: Observable<CodedConcept[]> = new Observable<CodedConcept[]>();
    public concepts: CodedConcept[] = [];
    public terminologySize!: number;
    public subsetSize!: number;
    public conceptsCount!: number;
    
    ngOnInit() {
        this.loadConcepts();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['terminology']) {
            this.loadConcepts();
        }
        if (changes['multiple']) {
            this.writeValue(null);
        }
    }

    loadConcepts() {
        this.concepts$ = this.terminologyService.getTerminologyConcepts({terminologyName: this.terminology}).pipe(map(
            (response: PaginatedCodedConcept) => {
                this.terminologySize = response.count;
                this.subsetSize = response.items.length;
                this.concepts = response.items;
                return response.items
            }
        )),        
        catchError(error => {
            console.error('Error loading terminology concepts:', error);
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error loading terminology concepts:' + error});
            return of([]); // Return empty array as fallback
        })
    }

    updateConcepts(event: {originalEvent: Event, query: string}) {
        this.concepts$ = this.terminologyService.getTerminologyConcepts({terminologyName: this.terminology, query: event.query}).pipe(
            map((response: PaginatedCodedConcept) => {
                this.subsetSize = response.items.length;
                this.concepts = response.items;
                return response.items
            }
        )),        
        catchError(error => {
            console.error('Error loading terminology concepts:', error);
            this.messageService.add({ severity: 'error', summary: 'Error', detail: 'Error loading terminology concepts:' + error});
            return of([]); // Return empty array as fallback
        })
    }

writeValue(value: any): void {
    if (this.returnCode) {
        if (value) {
            // Find the concept by code
            this.concepts$.pipe(first()).subscribe({
                next: (response) => {
                    if (this.multiple) {
                        this.formControl.patchValue(
                            value.map((val: string) => this.concepts.find(c => c.code === val))
                        );
                    } else {
                        this.formControl.patchValue(this.concepts.find(c => c.code === value));
                    }
                },
            })
        } else {
            this.formControl.patchValue(value);
        }
    } else {
        this.formControl.patchValue(value);
    }
}

registerOnChange(fn: any): void {
    this.formControl.valueChanges.subscribe((val) => {
        if (this.returnCode) {
            if (this.multiple) {
                fn(val ? val.map((c: CodedConcept) => c.code) : []);
            } else {
                fn(val ? val.code : null);
            }
        } else {
            fn(val);
        }
    });
}

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }

    conceptTrackBy(index: number, concept: CodedConcept) {
        return concept.code;
       }
}