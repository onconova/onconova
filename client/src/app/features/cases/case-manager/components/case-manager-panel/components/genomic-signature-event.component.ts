import { Component, ViewEncapsulation, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnyGenomicSignature } from 'onconova-api-client';

interface SignatureConfig {
    label: string;
    unit: string;
    threshold: number;
    max: number;
}

const SIGNATURE_CONFIGS: Record<string, SignatureConfig> = {
    tumor_mutational_burden:             { label: 'TMB', unit: 'Mut/Mb', threshold: 10,  max: 30  },
    loss_of_heterozygosity:              { label: 'LOH', unit: '%',       threshold: 15,  max: 100 },
    homologous_recombination_deficiency: { label: 'HRD', unit: '',        threshold: 42,  max: 100 },
};

@Component({
    selector: 'onconova-genomic-signature-event',
    encapsulation: ViewEncapsulation.None,
    template: `
        <div class="gs-event">
            @if (config()) {
                <div class="gs-label">
                    <span class="gs-label-text">{{ config()!.label }}</span>
                    @if (event()?.value !== undefined) {
                        <span class="gs-value">
                            {{ event()!.value | number:'1.0-1' }}{{ config()!.unit ? '\u202f' + config()!.unit : '' }}
                        </span>
                    }
                </div>
                @if (event()?.value !== undefined) {
                    <div class="gs-bar-container">
                        <div class="gs-bar">
                            <div class="gs-bar-segment gs-good-segment"
                                 [style.width.%]="(config()!.threshold / config()!.max) * 100"></div>
                            <div class="gs-bar-segment gs-bad-segment"
                                 [style.width.%]="((config()!.max - config()!.threshold) / config()!.max) * 100"></div>
                            <div class="gs-bar-indicator"
                                 [style.left.%]="clamp(event()!.value! / config()!.max * 100, 0, 100)">
                                <div class="gs-bar-circle"></div>
                            </div>
                        </div>
                        <div class="gs-bar-tick-row">
                            <div class="gs-bar-tick"
                                 [style.left.%]="(config()!.threshold / config()!.max) * 100">
                                <span>{{ config()!.threshold }}{{ config()!.unit ? '\u202f' + config()!.unit : '' }}</span>
                            </div>
                        </div>
                    </div>
                }
            } @else {
                <span class="gs-fallback">{{ event()?.description }}</span>
            }
        </div>
    `,
    imports: [CommonModule]
})
export class GenomicSignatureEventComponent {
    event = input<AnyGenomicSignature>();

    config = computed<SignatureConfig | null>(() => {
        const cat = this.event()?.category as string | undefined;
        return cat ? (SIGNATURE_CONFIGS[cat] ?? null) : null;
    });

    clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max);
}
