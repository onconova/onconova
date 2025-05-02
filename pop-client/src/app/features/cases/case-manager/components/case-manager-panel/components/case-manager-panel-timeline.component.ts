import { Component, Output, Signal, computed, inject, input } from '@angular/core';
import { EventEmitter } from '@angular/core';
import { CommonModule} from '@angular/common';
import { TimelineModule } from 'primeng/timeline';
import { TypeCheckService } from '../../../../../../shared/services/type-check.service';
import { Period } from '../../../../../../shared/openapi';

export interface RadioChoice {
    name: string 
    value: any
}

@Component({
    selector: 'pop-case-manager-panel-timeline',
    template: `
        <p-timeline [value]="groupedEvents()" class="case-manager-panel-timeline">
            <ng-template pTemplate="content" let-groupedEvents>
                <div>
                    <div class="pop-case-manager-panel-timeline-event-date mb-1">
                        <small>
                            @if (typeCheck.isPeriod(groupedEvents.timestamp)) {
                                {{ groupedEvents.timestamp.start | date }}
                                -
                                @if (groupedEvents.timestamp.end) {
                                    {{ groupedEvents.timestamp?.end | date }}
                                } @else {
                                    ongoing
                                }
                            } @else {
                                {{ groupedEvents.timestamp | date }}
                            }
                        </small>
                    </div>
                    <div class="flex flex-column gap-2">
                        @for (event of groupedEvents.events; track event.id) {
                            <div (click)="onEventClick.emit(event)" class="cursor-pointer">
                                <i class="pop-case-manager-panel-timeline-event-icon pi pi-box"></i>
                                {{ event.description }}
                            </div>                        
                        }
                    </div>
                </div>                    
            </ng-template>
        </p-timeline>
    `,
    imports: [
        CommonModule,
        TimelineModule,
    ]
})
export class CaseManagerPanelTimelineComponent {

    public readonly typeCheck = inject(TypeCheckService)

    @Output() public onEventClick = new EventEmitter<any>();
    public events = input.required<any[]>()
    public groupedEvents: Signal<{timestamp: Date | Period, events: any[]}[]> = computed(
        () => {
            let eventMap = this.events().map((event) => {
                let timestamp = event.period || event.assertionDate || event.date 
                return {
                    timestamp: timestamp,
                    event: event,
                }            
            });
            const uniqueTimeStamps = [...new Set(eventMap.map((event) => event.timestamp))];
            return uniqueTimeStamps.map((timestamp) => ({
                timestamp: timestamp,
                events: eventMap.filter((event) => event.timestamp == timestamp).map(event => event.event)
            }));
        }
    )
}