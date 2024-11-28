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

    @Input() control!: FormControl;

    constructor(private terminologyService: TerminologyService) {}

    ngOnInit() {
        this.terminologyService.getTerminologyConcepts(this.terminology).subscribe(
            (concepts: CodedConceptSchema[]) => {
                this.concepts = concepts;
            }
        );
    }

    filterConcepts(event: AutoCompleteCompleteEvent) {
        let filtered: any[] = [];
        let query = event.query;

        for (let i = 0; i < (this.concepts as any[]).length; i++) {
            let concept = (this.concepts as any[])[i];
            if (
                concept.display.toLowerCase().indexOf(query.toLowerCase()) == 0
                ||
                concept.code.toLowerCase().indexOf(query.toLowerCase()) == 0
            ) {
                filtered.push(concept);
            }
        }
        this.filteredConcepts = filtered;
    }
}