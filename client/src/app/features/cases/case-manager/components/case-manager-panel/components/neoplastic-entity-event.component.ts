import { Component, ViewEncapsulation, computed, input } from '@angular/core';
import { NeoplasticEntity } from 'onconova-api-client';
import { Chip } from 'primeng/chip';

@Component({
    selector: 'onconova-neoplastic-entity-event',
    encapsulation: ViewEncapsulation.None,
    template: `
        <div class="ne-event">
            <span class="ne-description">{{ event()?.description }}</span>
            <p-chip [label]="chipLabel()" [styleClass]="chipClass()"/>
        </div>
    `,
    imports: [Chip]
})
export class NeoplasticEntityEventComponent {
    event = input<NeoplasticEntity>();

    chipLabel = computed(() => {
        const rel = this.event()?.relationship ?? '';
        return rel.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    });

    chipClass = computed(() => {
        return this.event()?.relationship === 'primary'
            ? 'tag tag-primary ne-chip'
            : 'tag tag-primary-outline ne-chip';
    });
}
