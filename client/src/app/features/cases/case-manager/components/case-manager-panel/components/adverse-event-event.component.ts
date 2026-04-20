import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdverseEvent } from 'onconova-api-client';

const MITIGATION_LABELS: Record<string, string> = {
    pharmacological: 'pharmacologically',
    adjustment:      'by therapy adjustment',
    procedure:       'interventionally',
};

@Component({
    selector: 'onconova-adverse-event-event',
    template: `
        <div class="ae-event">
            <div class="ae-event-type">{{ eventType() }}</div>
            <div class="ae-event-sub">
                Grade {{ event()?.grade }}
                @if (suspectedCauseCount()) {
                    · {{ suspectedCauseCount() }} suspected cause{{ suspectedCauseCount() === 1 ? '' : 's' }}
                }
                @if (mitigationLabels().length) {
                    · Mitigated {{ mitigationLabels().join(', ') }}
                }
            </div>
        </div>
    `,
    imports: [CommonModule],
})
export class AdverseEventEventComponent {
    event = input<AdverseEvent>();

    eventType = computed(() => this.event()?.event?.display ?? this.event()?.description ?? '—');

    suspectedCauseCount = computed(() => this.event()?.suspectedCauses?.length ?? 0);

    mitigationLabels = computed((): string[] => {
        const mitigations = this.event()?.mitigations;
        if (!mitigations?.length) return [];
        const seen = new Set<string>();
        return mitigations
            .map(m => MITIGATION_LABELS[m.category] ?? m.category)
            .filter(label => {
                if (seen.has(label)) return false;
                seen.add(label);
                return true;
            });
    });
}
