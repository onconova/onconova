import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SystemicTherapy, Surgery, Radiotherapy } from 'onconova-api-client';
import { Chip } from 'primeng/chip';

@Component({
    selector: 'onconova-therapy-line-event',
    template: `
        @if (isSystemicTherapy()) {
            <div class="st-event">
                <div class="st-drugs">{{ drugNames() }}</div>
                <div class="st-meta">
                    @if (therapyLine()) {
                        <p-chip [label]="therapyLine()" styleClass="tag tag-primary-outline st-line-chip"/>
                    }
                    @if (cycles()) {
                        <span class="st-detail">{{ cycles() }} cycles</span>
                    }
                    @if (adjunctiveRole()) {
                        <span class="st-detail">{{ adjunctiveRole() }}</span>
                    }
                </div>
            </div>
        } @else {
            <div class="st-event">
                @if (fallbackDescription()) {
                    <div class="st-drugs">{{ fallbackDescription() }}</div>
                }
                @if (therapyLine()) {
                    <div class="st-meta">
                        <p-chip [label]="therapyLine()" styleClass="tag tag-primary-outline st-line-chip"/>
                    </div>
                }
            </div>
        }
    `,
    imports: [CommonModule, Chip]
})
export class TherapyLineEventComponent {

    event = input<SystemicTherapy | Surgery | Radiotherapy>();

    isSystemicTherapy = computed(() => 'medications' in (this.event() ?? {}));

    private get asSystemic(): SystemicTherapy {
        return this.event() as SystemicTherapy;
    }

    drugNames = computed(() => {
        const meds = this.asSystemic?.medications;
        if (!meds?.length) return this.event()?.description ?? '';
        return meds
            .map(m => m.drug?.properties?.['label'] || m.drug?.display || m.drug?.code)
            .filter(Boolean)
            .join('/');
    });

    therapyLine = computed(() => this.event()?.description.split(' - ')[0] ?? '');

    cycles = computed(() => this.asSystemic?.cycles ?? null);

    adjunctiveRole = computed(() => this.asSystemic?.adjunctiveRole?.display ?? null);

    fallbackDescription = computed(() => this.event()?.description.split(' - ')[1] ?? '');
}
