import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Lifestyle } from 'onconova-api-client';

interface LifestyleRow { label: string; value: string; }

@Component({
    selector: 'onconova-lifestyle-event',
    template: `
        <div class="lifestyle-event">
            @for (row of rows(); track row.label) {
                <div class="lifestyle-row">
                    <span class="lifestyle-label">{{ row.label }}</span>
                    <span class="lifestyle-value">{{ row.value }}</span>
                </div>
            }
        </div>
    `,
    imports: [CommonModule]
})
export class LifestyleEventComponent {
    event = input<Lifestyle>();

    rows = computed((): LifestyleRow[] => {
        const e = this.event();
        if (!e) return [];
        const rows: LifestyleRow[] = [];

        if (e.smokingStatus) {
            let val = e.smokingStatus.display ?? e.smokingStatus.code;
            const parts: string[] = [];
            if (e.smokingPackyears != null) parts.push(`${Math.round(e.smokingPackyears * 10) / 10} pack-yrs`);
            if (e.smokingQuited) {
                const yrs = (e.smokingQuited as any).year ?? (e.smokingQuited as any).value;
                if (yrs != null) parts.push(`quit ${Math.round(yrs * 10) / 10} yrs ago`);
            }
            if (parts.length) val += ` · ${parts.join(' · ')}`;
            rows.push({ label: 'Smoking', value: val });
        }

        if (e.alcoholConsumption) {
            rows.push({ label: 'Alcohol', value: e.alcoholConsumption.display ?? e.alcoholConsumption.code });
        }

        if (e.nightSleep != null) {
            const h = (e.nightSleep as any).hour ?? (e.nightSleep as any).value;
            if (h != null) rows.push({ label: 'Sleep', value: `${Math.round(h * 10) / 10} h/night` });
        }

        if (e.recreationalDrugs?.length) {
            rows.push({ label: 'Drugs', value: e.recreationalDrugs.map(d => d.display ?? d.code).join(', ') });
        }

        if (e.exposures?.length) {
            rows.push({ label: 'Exposures', value: e.exposures.map(x => x.display ?? x.code).join(', ') });
        }

        return rows;
    });
}
