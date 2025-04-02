import { Component, Input, inject } from '@angular/core';
import { CommonModule} from '@angular/common';
import { TimelineModule } from 'primeng/timeline';
import { TypeCheckService } from '../../services/type-check.service';
import { Period } from '../../openapi';

export interface RadioChoice {
    name: string 
    value: any
}

@Component({
    standalone: true,
    selector: 'pop-resource-timeline',
    template: `
        <p-timeline [value]="events" class="case-manager-panel-timeline">
            <ng-template pTemplate="content" let-event>
                <div>
                    <div class="case-manager-panel-timeline-date mb-1">
                        <small>
                            @if (typeCheck.isPeriod(event.timestamp)) {
                                {{ event.timestamp.start | date }}
                                -
                                @if (event.timestamp.end) {
                                    {{ event.timestamp?.end | date }}
                                } @else {
                                    ongoing
                                }
                            } @else {
                                {{ event.timestamp | date }}
                            }
                        </small>
                    </div>
                    <div class="flex flex-column gap-2">
                        @for (entry of event.entries; track entry.id) {
                            <div (click)="onEventClick(entry)" class="cursor-pointer">
                                <i class="pi pi-box" style="color: light-dark(var(--p-primary-900), var(--p-primary-100))"></i>
                                {{ entry.description }}
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
export class ResourceTimelineComponent {

    public readonly typeCheck = inject(TypeCheckService)

    @Input({required: true}) public entries: any[] = []
    @Input({required: true}) public onEventClick!: (event: any) => void;
    public events: {timestamp: Date | Period, entries: any[]}[] = []
    
    ngOnInit() {
        let eventMap = this.entries.map((entry) => {
            let timestamp = entry.period || entry.assertionDate || entry.date 
            return {
                timestamp: timestamp,
                entry: entry,
            }            
        });
        const uniqueTimeStamps = [...new Set(eventMap.map((event) => event.timestamp))];
        this.events = uniqueTimeStamps.map((timestamp) => ({
            timestamp: timestamp,
            entries: eventMap.filter((event) => event.timestamp == timestamp).map(event => event.entry)
        }));
    }
}