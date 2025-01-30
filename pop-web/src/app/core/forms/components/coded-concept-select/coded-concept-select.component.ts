import { inject, Component, Input, forwardRef, DestroyRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { TerminologyService } from '../../../../shared/openapi/api/terminology.service';
import { CodedConceptSchema, PaginatedCodedConceptSchema } from '../../../../shared/openapi';
import { Observable, map, of } from 'rxjs';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { Button } from 'primeng/button';
import { RadioButton } from 'primeng/radiobutton';
import { ReactiveFormsModule } from '@angular/forms';

interface AutoCompleteCompleteEvent {
    originalEvent: Event;
    query: string;
}

@Component({
    standalone: true,
    selector: 'coded-concept-select',
    styleUrl: './coded-concept-select.component.css',
    templateUrl: './coded-concept-select.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => CodedConceptSelectComponent),
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
export class CodedConceptSelectComponent implements ControlValueAccessor {
    
    private terminologyService: TerminologyService = inject(TerminologyService);

    @Input() terminology!: string;
    @Input() formControlName!: string;
    @Input() showSynonyms: boolean = true;
    @Input() showCodes: boolean = false;
    @Input() multiple: boolean = false;
    @Input() baseQuery: string = '';
    @Input() placeholder: string = 'Select or search an option';
    @Input() conceptsLimit: number = 100;
    @Input() widget: 'autocomplete' | 'radio' = 'autocomplete';

    public formControl: FormControl = new FormControl();
    public concepts$!: Observable<CodedConceptSchema[]>;
    public concepts: CodedConceptSchema[] = [];
    public terminologySize!: number;
    public subsetSize!: number;
    public conceptsCount!: number;
    
    ngOnInit() {
        this.concepts$ = this.terminologyService.getTerminologyConcepts({terminologyName: this.terminology}).pipe(map(
            (response: PaginatedCodedConceptSchema) => {
                this.terminologySize = response.count;
                this.subsetSize = response.items.length;
                this.concepts = response.items;
                return response.items
            }
        ))
    }

    updateConcepts(event: AutoCompleteCompleteEvent) {
        let query: string = this.baseQuery ? `${this.baseQuery}${event.query}` : event.query; 
        this.concepts$ = this.terminologyService.getTerminologyConcepts({terminologyName: this.terminology, query: query}).pipe(map(
            (response: PaginatedCodedConceptSchema) => {
                this.subsetSize = response.items.length;
                this.concepts = response.items, query
                return response.items
            }
        ))
    }

    writeValue(value: any): void {
        this.formControl.patchValue(value);
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => fn(val));
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }

    conceptTrackBy(index: number, concept: CodedConceptSchema) {
        return concept.code;
       }
}