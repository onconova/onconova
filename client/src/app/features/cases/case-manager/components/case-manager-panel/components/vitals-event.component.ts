import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Vitals } from 'onconova-api-client';

interface VitalMetric {
    label: string;
    display: string;
    percentage: number;
}

// Physiological reference ranges used for normalizing the dot position.
const RANGES: Record<string, { min: number; max: number }> = {
    weight:               { min: 0,   max: 200 },
    height:               { min: 100, max: 220 },
    bloodPressureSysolic: { min: 60,  max: 220 },
    bloodPressureDiastolic: { min: 40, max: 140 },
    temperature:          { min: 35,  max: 42  },
    bodyMassIndex:        { min: 10,  max: 50  },
};

function normalize(value: number, rangeKey: string): number {
    const r = RANGES[rangeKey];
    if (!r) return 50;
    return Math.min(100, Math.max(2, ((value - r.min) / (r.max - r.min)) * 100));
}

@Component({
    selector: 'onconova-vitals-event',
    template: `
        @if (graphMode()) {
            <div class="vitals-dotline">
                @for (metric of chartMetrics(); track metric.label) {
                    <div class="vitals-dotline-row">
                        <span class="vitals-dotline-label">{{ metric.label }}</span>
                        <div class="vitals-dotline-track">
                            <div class="vitals-dotline-fill" [style.width.%]="metric.percentage"></div>
                            <div class="vitals-dotline-dot" [style.left.%]="metric.percentage"></div>
                        </div>
                        <span class="vitals-dotline-value">{{ metric.display }}</span>
                    </div>
                }
                @if (!chartMetrics().length) {
                    <span class="vitals-no-measurements">{{ event()?.description }}</span>
                }
            </div>
        } @else {
            <div class="vitals-list">
                @for (metric of chartMetrics(); track metric.label) {
                    <div class="vitals-list-row">
                        <span class="vitals-list-label">{{ metric.label }}</span>
                        <span class="vitals-list-value">{{ metric.display }}</span>
                    </div>
                }
                @if (!chartMetrics().length) {
                    <span>{{ event()?.description }}</span>
                }
            </div>
        }
    `,
    imports: [CommonModule],
})
export class VitalsEventComponent {
    event = input<Vitals>();
    graphMode = input<boolean>(false);

    chartMetrics = computed((): VitalMetric[] => {
        const v = this.event();
        if (!v) return [];
        const metrics: VitalMetric[] = [];

        if (v.weight) metrics.push({
            label: 'Weight',
            display: `${v.weight.value} ${v.weight.unit}`,
            percentage: normalize(v.weight.value, 'weight'),
        });
        if (v.height) metrics.push({
            label: 'Height',
            display: `${v.height.value} ${v.height.unit}`,
            percentage: normalize(v.height.value, 'height'),
        });
        if (v.bloodPressureSystolic && v.bloodPressureDiastolic) {
            metrics.push({
                label: 'BP',
                display: `${v.bloodPressureSystolic.value}/${v.bloodPressureDiastolic.value} ${v.bloodPressureSystolic.unit}`,
                percentage: normalize(v.bloodPressureSystolic.value, 'bloodPressureSysolic'),
            });
        } else if (v.bloodPressureSystolic) {
            metrics.push({
                label: 'Systolic',
                display: `${v.bloodPressureSystolic.value} ${v.bloodPressureSystolic.unit}`,
                percentage: normalize(v.bloodPressureSystolic.value, 'bloodPressureSysolic'),
            });
        } else if (v.bloodPressureDiastolic) {
            metrics.push({
                label: 'Diastolic',
                display: `${v.bloodPressureDiastolic.value} ${v.bloodPressureDiastolic.unit}`,
                percentage: normalize(v.bloodPressureDiastolic.value, 'bloodPressureDiastolic'),
            });
        }
        if (v.temperature) metrics.push({
            label: 'Temp',
            display: `${v.temperature.value} ${v.temperature.unit}`,
            percentage: normalize(v.temperature.value, 'temperature'),
        });
        if (v.bodyMassIndex) metrics.push({
            label: 'BMI',
            display: `${v.bodyMassIndex.value.toPrecision(3)} ${v.bodyMassIndex.unit.replace('__', '/').replace('square_meter', 'm²')}`,
            percentage: normalize(v.bodyMassIndex.value, 'bodyMassIndex'),
        });

        return metrics;
    });
}
