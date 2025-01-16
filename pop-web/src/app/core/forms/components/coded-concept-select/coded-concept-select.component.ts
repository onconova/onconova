import { inject, Component, Input, forwardRef, DestroyRef } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { TerminologyService } from '../../../../shared/openapi/api/terminology.service';
import { CodedConceptSchema } from '../../../../shared/openapi';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { Button } from 'primeng/button';
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


    public formControl: FormControl = new FormControl();
    public concepts!: CodedConceptSchema[];
    public filteredConcepts!: CodedConceptSchema[];
    public conceptsCount!: number;
    public conceptsLimit: number = 100;
    private readonly destroyRef = inject(DestroyRef);
    
    ngOnInit() {
        this.getTerminologyConcepts()
    }

    getTerminologyConcepts() {
        this.terminologyService.getTerminologyConcepts(this.terminology)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
            next: data => {
                this.concepts = data.items;
                this.filteredConcepts = this.concepts;
                this.conceptsCount = data.count;
            }
        });
    }

    filterConcepts(event: AutoCompleteCompleteEvent) {
        let query: string = this.baseQuery ? `${this.baseQuery}${event.query}` : event.query; 
        this.getTerminologyConcepts()
        if (query != '') {
            if (query && this.conceptsCount >= this.conceptsLimit) {
                this.terminologyService.getTerminologyConcepts(this.terminology, query)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({            
                    next: data => {                    
                        this.filteredConcepts = this.filterAndSortConcepts(data.items, query);
                        this.conceptsCount = data.count;
                    }
                })
            } else {
                this.filteredConcepts = this.filterAndSortConcepts(this.concepts, query)
            }
        }
    }


    filterAndSortConcepts(concepts: CodedConceptSchema[], query: string) {
        let filteredConcepts = [...concepts];
        if (query != '') {
            // Calculate the scores
            let scores: number[] = concepts.map((concept) => this.conceptQueryMatchingScore(concept, query.toLowerCase()));
            // Filter the concepts based on non-zero scores
            filteredConcepts = concepts.filter((_, index) => scores[index] > 0);
            // Sort the filtered concepts in descending order of score
            filteredConcepts.sort((a, b) => scores[concepts.indexOf(b)] - scores[concepts.indexOf(a)]);
        } 
        console.log('FILTERED', filteredConcepts.length)
        return filteredConcepts
    }
 
    conceptQueryMatchingScore(concept: CodedConceptSchema, query: string): number {
        // Scores to prioritize concept matching
        const codeScore = 10;
        const displayScore = 5;
        const synonymScore = 1;
        // Go over each word in the query string and accumulate the score value based on matches
        let score: number  = 0;
        query.split(' ').forEach(word => {
            if (word) {
                score += (concept.code.toLowerCase().includes(word) ? codeScore: 0)
                + 
                ((concept.display != null && concept.display.toLowerCase().includes(word)) ? displayScore: 0)
                +
                ((concept.synonyms != null && concept.synonyms.some((synonym:string) => synonym.toLowerCase().includes(word))) ? synonymScore: 0);
            }
        })   
        return score
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