import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NeoplasticEntity } from 'onconova-api-client';

/**
 * Custom event component for displaying neoplastic entities in the timeline.
 * Renders the topography, morphology, and relationship information in a compact format.
 */
@Component({
    selector: 'onconova-multiline-event',
    template: `
        <div *ngFor="let item of items()">
            {{ item }}
        </div>
    `,
    imports: [CommonModule]
})
export class MultilineEventComponent {
    /**
     * The neoplastic entity event data to display
     */
    event = input<NeoplasticEntity>();
    items = computed(() => {
        return this.event()?.description.split('\n') || [];
    })
}
