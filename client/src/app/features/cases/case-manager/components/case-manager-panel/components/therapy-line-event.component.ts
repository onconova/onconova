import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SystemicTherapy, Surgery, Radiotherapy } from 'onconova-api-client';
import { Chip } from 'primeng/chip';
/**
 * Custom event component for displaying neoplastic entities in the timeline.
 * Renders the topography, morphology, and relationship information in a compact format.
 */
@Component({
    selector: 'onconova-therapy-line-event',
    template: `
        <div>
            <p-chip [label]="therapyLine()" styleClass="tag tag-primary-outline"/>
            {{ description() }}
        </div>
    `,
    imports: [CommonModule, Chip]
})
export class TherapyLineEventComponent {

    event = input<SystemicTherapy | Surgery | Radiotherapy>();
    therapyLine = computed(() => {
        return this.event()?.description.split(' - ')[0] || '';
    })
    description = computed(() => {
        return this.event()?.description.split(' - ')[1] || '';
    })
}
