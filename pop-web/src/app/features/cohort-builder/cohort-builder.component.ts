import { NgModule, Component, Input, ViewEncapsulation, OnInit, inject, DestroyRef,ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, first, of, map, startWith} from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { CodedConceptSelectComponent } from 'src/app/core/forms/components';

import { CohortsService } from 'src/app/shared/openapi';

import { Button } from 'primeng/button';
import { RadioButton } from 'primeng/radiobutton';
import { SelectButton } from 'primeng/selectbutton';

import { NgxAngularQueryBuilderModule, QueryBuilderConfig, Field } from "ngx-angular-query-builder";

@Component({
    standalone: true,
    selector: 'app-cohort-builder',
    templateUrl: './cohort-builder.component.html',
    encapsulation: ViewEncapsulation.None,
    imports: [
        CommonModule,
        FormsModule,
        NgxAngularQueryBuilderModule,
        Button,
        RadioButton,
        SelectButton,
        CodedConceptSelectComponent,
        
    ]
})
export class CohortBuilderComponent {

    private cohortsService = inject(CohortsService);

    public readonly rulesetConditions = [
        {value: 'and', label: 'AND'},
        {value: 'or', label: 'OR'},
    ]

    public query!: any;

    config$ = this.cohortsService.getCohortBuilderConfig();

}
