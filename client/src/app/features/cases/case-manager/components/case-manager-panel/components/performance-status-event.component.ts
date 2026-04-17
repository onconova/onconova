import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PerformanceStatus } from 'onconova-api-client';

interface DotInfo { index: number; active: boolean; }

@Component({
    selector: 'onconova-performance-status-event',
    template: `
        <div class="ps-event">
            @if (ecogScore() !== null) {
                <div class="ps-row">
                    <span class="ps-label">ECOG</span>
                    <div class="ps-track">
                        @for (dot of ecogDots(); track dot.index) {
                            <span class="ps-dot" [class.active]="dot.active"></span>
                        }
                        <span class="ps-score">{{ ecogScore() }}</span>
                    </div>
                </div>
            } @else if (kpsScore() !== null) {
                <div class="ps-row">
                    <span class="ps-label">KPS</span>
                    <div class="ps-track">
                        @for (dot of kpsDots(); track dot.index) {
                            <span class="ps-dot" [class.active]="dot.active"></span>
                        }
                        <span class="ps-score">{{ kpsScore() }}</span>
                    </div>
                </div>
            }
        </div>
    `,
    imports: [CommonModule]
})
export class PerformanceStatusEventComponent {
    event = input<PerformanceStatus>();

    ecogScore = computed(() => this.event()?.ecogScore ?? null);
    kpsScore  = computed(() => this.event()?.karnofskyScore ?? null);

    ecogDots = computed((): DotInfo[] => {
        const score = this.ecogScore();
        if (score === null) return [];
        return Array.from({ length: 6 }, (_, i) => ({ index: i, active: i === score }));
    });

    kpsDots = computed((): DotInfo[] => {
        const score = this.kpsScore();
        if (score === null) return [];
        return Array.from({ length: 11 }, (_, i) => ({ index: i, active: i * 10 === score }));
    });
}
