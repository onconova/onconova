import { Component, computed, contentChild, inject, TemplateRef } from '@angular/core';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { CardModule } from 'primeng/card';
import { RandomPaperComponent } from './components/random-paper.component';

import { PrimaryEntitiesTableComponent } from './components/primary-entities-table.component';
import { DataSummaryComponent } from './components/data-summary.component';
import { GetFullNamePipe } from 'src/app/shared/pipes/full-name.pipe';

import { CommonModule } from '@angular/common';
import { DisclaimerBannerComponent } from "./components/disclaimer-banner.component";
import { DataCompletionStatsComponent } from './components/data-completion.component';

@Component({
    selector: 'pop-dashboard',
    imports: [
        CommonModule,
        InlineSVGModule,
        CardModule,
        RandomPaperComponent,
        DataSummaryComponent,
        PrimaryEntitiesTableComponent,
        DataCompletionStatsComponent,
        DisclaimerBannerComponent,
        GetFullNamePipe,
    ],
    template: `
    <h3 class="mb-5 font-semibold">Good {{ greet.toLowerCase() }}, {{ user() | fullname }}!</h3>
    <div class="grid grid-nested">
        <div class=" col-12 md:col-7 lg:col-7">
            <div class="grid">
                <div class="col-12">
                    <pop-disclaimer-banner/>
                </div>
                <div class="col-12">
                    <p-card styleClass="">
                        <div class="mb-3">
                            <h5 class="mb-0 font-semibold">Primary Sites</h5>
                            <div class="text-muted">A summary of the existing cases classified by primary sites and their completion status</div>
                        </div>
                        <pop-primary-entities-table/>
                    </p-card>
                </div>
                <div class="col-12">
                    <p-card styleClass="">
                        <div class="mb-3">
                            <h5 class="mb-0 font-semibold">Data Collection</h5>
                            <div class="text-muted">A measure of the overall data collection efforts of the platform</div>
                        </div>
                        <pop-data-completion-stats/>
                    </p-card>
                </div>
            </div>
        </div>
        <div class="col-12 md:col-5 lg:col-5 ">
            @if (additionalPanelsTemplate(); as template) {
                <ng-container *ngTemplateOutlet="template"></ng-container>
            }
            <p-card styleClass="">
                <div class="mb-3">
                    <h5 class="mb-0 font-semibold">Data Platform Summary</h5>
                    <div class="text-muted">A summary of the current state of the data platform</div>
                </div>
                <pop-data-summary/>
            </p-card>
            <p-card styleClass="mt-3">
                <div class="mb-3">
                    <h5 class="mb-0 font-semibold">Paper of the Day - {{ today | date }}</h5>
                    <div class="text-muted">A random selection from recent oncology publications to read today</div>
                </div>
                <pop-random-paper/>
            </p-card>
        </div>
    </div>
    `
})
export class DashboardComponent {

    readonly #authService = inject(AuthService);
    
    public additionalPanelsTemplate = contentChild<TemplateRef<any>>('additionalPanels', { descendants: false });
    public today = new Date();
    private hours = this.today.getHours()
    public greet =  (this.hours >= 5 && this.hours < 12) ? "Morning" : (this.hours >= 12 && this.hours < 17) ? "Afternoon" : (this.hours >= 17 && this.hours < 20) ? "Evening" : "Night";
    public user = computed(() => this.#authService.user()); 

    
}
