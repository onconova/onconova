import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NeoplasticEntity } from 'onconova-api-client';
import { Chip } from 'primeng/chip';

/**
 * Custom event component for displaying neoplastic entities in the timeline.
 * Renders the topography, morphology, and relationship information in a compact format.
 */
@Component({
    selector: 'onconova-neoplastic-entity-event',
    template: `
        <div class="onconova-neoplastic-entity-event">
            <div class="onconova-neoplastic-entity-event-content">
                <div class="onconova-neoplastic-entity-event-main">
                
                    <p-chip [label]="category() | titlecase" styleClass="tag tag-primary"/>
                </div>
                <div class="onconova-neoplastic-entity-event-details">
                    {{ description() }}
                </div>
            </div>
        </div>
    `,
    styles: [`
        .onconova-neoplastic-entity-event {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .onconova-neoplastic-entity-event-content {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .onconova-neoplastic-entity-event-main {
            font-weight: 500;
            color: var(--text-color);
        }

        .onconova-neoplastic-entity-event-details {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .onconova-neoplastic-entity-event-detail {
            display: flex;
            gap: 0.25rem;
            align-items: center;
            font-size: 0.875rem;
        }

        .onconova-neoplastic-entity-event-laterality,
        .onconova-neoplastic-entity-event-differentiation {
            display: flex;
            gap: 0.25rem;
            font-size: 0.875rem;
        }

        small.text-muted {
            color: var(--text-color-secondary);
            font-weight: 500;
        }
    `],
    imports: [CommonModule, Chip]
})
export class NeoplasticEntityEventComponent {
    /**
     * The neoplastic entity event data to display
     */
    event = input<NeoplasticEntity>();
    category = computed(() => {
            return this.event()!.relationship.replace('_', ' ');
    })
    description = computed(() => {
        const capitalizedCategory = this.category()[0].toUpperCase() + this.category().slice(1);
        let description = this.event()!.description.replace(capitalizedCategory, '');
        description = description.replace(/^\s/, ''); // Remove leading dash if present
        description = description[0].toUpperCase() + description.slice(1);
        console.log(description)
        return description;
    });
}
