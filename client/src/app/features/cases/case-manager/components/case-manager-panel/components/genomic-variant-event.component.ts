import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GenomicVariant } from 'onconova-api-client';

/**
 * Compact custom event component for displaying genomic variants in the timeline.
 * Shows gene name, HGVS notation, clinical significance, and optional VAF/consequence.
 */
@Component({
    selector: 'onconova-genomic-variant-event',
    template: `
        <div class="genomic-variant-event">
            <div class="variant-main-row">
                @if (geneLabel()) {
                    <span class="variant-gene">{{ geneLabel() }}</span>
                }
                @if (hgvs()) {
                    <span class="variant-hgvs">{{ hgvs() }}</span>
                }
                @if (significanceLabel()) {
                    <span class="variant-significance">{{ significanceLabel() }}</span>
                }
            </div>
            @if (subInfo()) {
                <div class="variant-sub-row">{{ subInfo() }}</div>
            }
        </div>
    `,
    imports: [CommonModule]
})
export class GenomicVariantEventComponent {
    event = input<GenomicVariant>();

    geneLabel = computed(() => {
        const genes = this.event()?.genes;
        if (!genes?.length) return null;
        const labels = genes.map(g => g.properties?.['symbol'] || g.display || g.code);
        return labels.length > 2 ? labels.slice(0, 2).join(', ') + '…' : labels.join(', ');
    });

    hgvs = computed(() => {
        const raw = this.event()?.proteinHgvs || this.event()?.dnaHgvs || null;
        if (!raw) return null;
        const match = raw.match(/:(?:p|c|g)\.(.+)$/);
        return match ? match[1] : raw;
    });

    significanceLabel = computed(() => {
        const r = this.event()?.clinicalRelevance;
        return r === 'uncertain_significance' ? 'VUS' : null;
    });

    subInfo = computed(() => {
        const parts: string[] = [];
        const vaf = this.event()?.alleleFrequency;
        if (vaf != null) parts.push(`VAF ${(vaf * 100).toFixed(1)}%`);
        const mc = this.event()?.molecularConsequence?.display;
        if (mc) parts.push(mc);
        return parts.join(' · ') || null;
    });
}
