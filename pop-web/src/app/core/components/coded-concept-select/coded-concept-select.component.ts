import { Component, Input, forwardRef } from '@angular/core';
import { NG_VALUE_ACCESSOR } from '@angular/forms';
import { TerminologyService } from '../../../core/modules/openapi/api/terminology.service';
import { CodedConceptSchema } from '../../../core/modules/openapi';
import {FormControl} from '@angular/forms';

interface AutoCompleteCompleteEvent {
    originalEvent: Event;
    query: string;
}
@Component({
    selector: 'coded-concept-select',
    templateUrl: './coded-concept-select.component.html',
    providers:[
        TerminologyService,
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => CodedConceptSelectComponent),
            multi: true
        }
    ]
})
export class CodedConceptSelectComponent {
    @Input() terminology!: string;
    @Input() formControlName!: string;
    @Input() showSynonyms: boolean = true;
    @Input() showCodes: boolean = false;
    concepts: CodedConceptSchema[] = [];
    filteredConcepts: CodedConceptSchema[] = [];

    @Input() baseQuery: string = '';
    @Input() control!: FormControl | any;

    constructor(private terminologyService: TerminologyService) {}

    ngOnInit() {
        this.terminologyService.getTerminologyConcepts(this.terminology).subscribe(
            (concepts: CodedConceptSchema[]) => {
                this.concepts = concepts;
            }
        );
    }

    filterConcepts(event: AutoCompleteCompleteEvent) {
        let query: string = `${this.baseQuery} ${event.query}`
        this.filteredConcepts = this.concepts;
        query.split(' ').forEach(word => {
            if (word) {
                this.filteredConcepts = this.filteredConcepts.filter((concept) => this.conceptMatchesQuery(concept, word.toLowerCase()));
            }
        })
    }

    conceptMatchesQuery(concept: CodedConceptSchema, query: string): boolean {
        return concept.code.toLowerCase().includes(query)
            || 
            concept.display != null && concept.display.toLowerCase().includes(query)
            ||
            (concept.synonyms != null && concept.synonyms.some((synonym:string) => synonym.toLowerCase().includes(query)));   
    }
}