import { inject, Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { TerminologyService } from '../../../../core/modules/openapi/api/terminology.service';
import { CodedConceptSchema } from '../../../../core/modules/openapi';
import { Subscription } from 'rxjs';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ReactiveFormsModule } from '@angular/forms';

interface AutoCompleteCompleteEvent {
    originalEvent: Event;
    query: string;
}

@Component({
    standalone: true,
    selector: 'coded-concept-select',
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


    public formControl: FormControl = new FormControl();
    public concepts!: CodedConceptSchema[];
    public filteredConcepts!: CodedConceptSchema[];
    private conceptsSubscription!: Subscription;


    ngOnInit() {
        this.conceptsSubscription = this.terminologyService.getTerminologyConcepts(this.terminology).subscribe({
            next: data => {
                this.concepts = data;
                this.filteredConcepts = data;
            }
        });

    }

    filterConcepts(event: AutoCompleteCompleteEvent) {
        let filtered: CodedConceptSchema[] = []
        let query: string = `${this.baseQuery} ${event.query}`
        filtered = [...this.concepts];
        query.split(' ').forEach(word => {
            if (word) {
                filtered = filtered.filter((concept) => this.conceptMatchesQuery(concept, word.toLowerCase()));
            }
        })
        this.filteredConcepts = filtered
    }

 
    conceptMatchesQuery(concept: CodedConceptSchema, query: string): boolean {
        return concept.code.toLowerCase().includes(query)
            || 
            concept.display != null && concept.display.toLowerCase().includes(query)
            ||
            (concept.synonyms != null && concept.synonyms.some((synonym:string) => synonym.toLowerCase().includes(query)));   
    }


    ngOnDestroy(): void {
        this.conceptsSubscription.unsubscribe();
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