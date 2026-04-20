import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TumorMarker } from 'onconova-api-client';

/**
 * Custom event component for displaying tumor markers in the timeline.
 * Renders the tumor marker with a color bar indicator showing value ranges.
 */
@Component({
    selector: 'onconova-tumor-marker-event',
    template: `
        <div class="onconova-tumor-marker-event">
            <div class="label">
                <div class="label-text">
                    @if (event()?.analyte?.properties; as props) {
                        {{ props['acronym'] || props['name'] || 'Unknown Marker' }}:
                    }
                </div>
                @if (quantityValue() !== null) {
                    <div class="value">
                        {{ quantityValue()?.value | number:'1.0-2' }} {{ quantityValue()?.unit?.replace('__', '/') }}
                    </div>
                } 
                @if (categoryValue() !== null) {
                    <div class="value">
                        {{ categoryValue() }}
                    </div>
                } 
            </div>
            @if (quantityValue() !== null && quantityValue()?.unit?.replace('__', '/') == thresholdUnit() && lowThreshold() !== undefined && highThreshold() !== undefined) {
                <div class="flex-grow-1"></div>
                <div class="bar-container ">
                    <div class="bar">
                        <div class="bar-segment bad-segment" 
                             [style.width.%]="(lowThreshold()! / maxValue()) * 100"></div>
                        <div class="bar-segment good-segment" 
                             [style.width.%]="((highThreshold()! - lowThreshold()!) / maxValue()) * 100"></div>
                        <div class="bar-segment bad-segment" 
                             [style.width.%]="((maxValue()! - highThreshold()!) / maxValue()) * 100"></div>
                        <div class="bar-indicator" 
                             [style.left.%]="max(min((quantityValue()?.value! / maxValue()) * 100, 100), 0)">
                            <div class="bar-circle"></div>
                        </div>
                    </div>
                    <div class="bar-labels text-muted">
                        <span>{{ lowThreshold() }}</span>
                        <span>{{ highThreshold() }}</span>
                        <span>{{ maxValue() }}</span>
                    </div>
                </div>
            }
        </div>
    `,
    imports: [CommonModule]
})
export class TumorMarkerEventComponent {
    /**
     * The tumor marker event data to display
     */
    event = input<TumorMarker>();

    /**
     * Extracts numeric value from the tumor marker
     */
    quantityValue = computed(() => {
        const marker = this.event();
        if (!marker) return null;

        // Try to extract numeric value from various fields
        if (marker.fraction?.value !== undefined) {
            return marker.fraction;
        }
        if (marker.combinedPositiveScore?.value !== undefined) {
            return marker.combinedPositiveScore;
        }
        if (marker.massConcentration?.value !== undefined) {
            return marker.massConcentration;
        }
        if (marker.arbitraryConcentration?.value !== undefined) {
            return marker.arbitraryConcentration;
        }
        if (marker.substanceConcentration?.value !== undefined) {
            return marker.substanceConcentration;
        }
        if (marker.multipleOfMedian?.value !== undefined) {
            return marker.multipleOfMedian;
        }
        if (marker.multipleOfMedian?.value !== undefined) {
            return marker.multipleOfMedian;
        }

        return null;
    });

    categoryValue = computed(() => {
        const marker = this.event();
        if (!marker) return null;
        // Try to extract category value from various fields
        if (marker.tumorProportionScore) {
            return marker.tumorProportionScore;
        }
        if (marker.immuneCellScore) {
            return marker.immuneCellScore;
        }
        if (marker.immunohistochemicalScore) {
            return marker.immunohistochemicalScore;
        }
        if (marker.nuclearExpressionStatus) {
            return marker.nuclearExpressionStatus;
        }
        if (marker.presence) {
            return marker.presence;
        }
        return null;
    });

    private tumorMarkerRanges: Record<string, { low: number; high: number; unit: string, max?: number }> = {
        'Ki67': { low: 5, high: 20, unit: "%" },
        'AFP': { low: 0, high: 10, unit: "ng/ml" },
        'CEA': { low: 0, high: 5, unit: "ng/ml" },
        'CA125': { low: 0, high: 35, unit: "kIU/l" },
        'CA15-3': { low: 0, high: 30, unit: "kIU/l" },
        'CA19-9': { low: 0, high: 37, unit: "kIU/l" },
        'CA242': { low: 0, high: 20, unit: "kIU/l" },
        'CA27-29': { low: 0, high: 38, unit: "kIU/l" },
        'CA50': { low: 0, high: 25, unit: "kIU/l" },
        'CA549': { low: 0, high: 11, unit: "kIU/l" },
        'CA72-4': { low: 0, high: 6.9, unit: "kIU/l" },
        'CTC': { low: 0, high: 0, unit: "kIU/l" },
        'FGF': { low: 0, high: 0.01, unit: "ng/ml" },
        'FGF-23': { low: 0.01, high: 0.05, unit: "ng/ml" },
        'GRP': { low: 0, high: 0.05, unit: "ng/ml" },
        'TNFBP1': { low: 0.5, high: 3, unit: "ng/ml" },
        'YKL-40': { low: 0, high: 60, unit: "ng/ml" },
        'NSE': { low: 0, high: 16.3, unit: "ng/ml" },
        'LDH': { low: 140, high: 0.280, unit: "kIU/l" },
        'CgA': { low: 0, high: 100, unit: "ng/ml" },
        'S100B': { low: 0, high: 0.1, unit: "µg/L" },
        'PSA': { low: 0, high: 4, unit: "ng/ml" },
        'β-hCG': { low: 0, high: 0.005, unit: "kIU/l" },
        'CYFRA 21-1': { low: 0, high: 3.3, unit: "ng/ml" },
        'HE4': { low: 0, high: 140, unit: "pmol/L" },
        'EBV DNA': { low: 0, high: 200, unit: "kIU/l" }
    }

    threshold = computed(() => {
        const marker = this.event();
        if (!marker || !marker.analyte?.properties) return undefined;

        const acronym: keyof typeof this.tumorMarkerRanges = marker.analyte?.properties['acronym'];
        if (acronym && this.tumorMarkerRanges[acronym]) {
            return this.tumorMarkerRanges[acronym];
        }
        return undefined
    });
    thresholdUnit = computed(() => this.threshold()?.unit);
    lowThreshold = computed(() => this.threshold()?.low);
    highThreshold = computed(() => this.threshold()?.high);
    maxValue = computed(() => {
        const threshold = this.threshold();
        if (threshold) {
            return threshold.max ?? threshold.high * 2; // Set max value to 250% of high threshold for better visualization
        }
        return 100; // Default max value
    });




    max = (x: number, y: number) => {
        return Math.max(x, y);
    }
    min = (x: number, y: number) => {
        return Math.min(x, y);
    }



}
