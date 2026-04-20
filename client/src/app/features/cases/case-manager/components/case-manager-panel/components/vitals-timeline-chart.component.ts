import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Vitals } from 'onconova-api-client';

// ── Layout constants (viewBox coordinate space) ──────────────────────────────
const VB_W    = 400;
const ML      = 62;   // left margin (series labels)
const MR      = 10;   // right margin
const MT      = 6;    // top margin
const MB      = 24;   // bottom margin (date labels)
const BAND_H  = 96;   // ~6rem per series band
const BAND_P  = 10;   // inner padding within a band
const BAND_GAP = 14;  // whitespace between subplots
const DOT_R   = 3.5;  // dot radius
const CHART_W = VB_W - ML - MR;

// ── Series definitions ────────────────────────────────────────────────────────
const SERIES_DEFS: { key: keyof Vitals; label: string; range: [number, number] }[] = [
    { key: 'weight',                 label: 'Weight',    range: [30,  150] },
    { key: 'height',                 label: 'Height',    range: [140, 210] },
    { key: 'bloodPressureSystolic',  label: 'Systolic',  range: [80,  200] },
    { key: 'bloodPressureDiastolic', label: 'Diastolic', range: [40,  130] },
    { key: 'temperature',            label: 'Temp',      range: [35,  42]  },
    { key: 'bodyMassIndex',          label: 'BMI',       range: [15,  45]  },
];

// ── Types ─────────────────────────────────────────────────────────────────────
interface ChartPoint { x: number; y: number; event: Vitals; display: string; }
interface YTick     { y: number; value: string; }
interface ChartSeries {
    label: string;
    bandY: number;
    points: (ChartPoint | null)[];
    continuousPath: string;
    yTicks: YTick[];           // 2 horizontal reference lines + labels
}
interface ClickZone { x1: number; x2: number; xi: number; event: Vitals | null; }
interface ChartData {
    viewBox: string;
    totalH: number;
    innerH: number;
    dates: { x: number; label: string }[];
    series: ChartSeries[];
    clickZones: ClickZone[];
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function clampNorm(value: number, range: [number, number]): number {
    const [lo, hi] = range;
    return Math.min(1, Math.max(0, (value - lo) / (hi - lo)));
}

function shortDate(dateStr: string): string {
    const d = new Date(dateStr);
    return `${d.getDate()}/${d.getMonth() + 1}/${String(d.getFullYear()).slice(2)}`;
}

// ── Component ─────────────────────────────────────────────────────────────────
@Component({
    selector: 'onconova-vitals-timeline-chart',
    template: `
        @if (chart().series.length) {
            <svg class="vitals-chart-svg"
                 [attr.viewBox]="chart().viewBox"
                 width="100%"
                 [attr.height]="chart().totalH">

                <!-- Band backgrounds (alternating) -->
                @for (s of chart().series; track s.label; let si = $index) {
                    <rect [attr.x]="ML" [attr.y]="s.bandY"
                          [attr.width]="CHART_W" [attr.height]="BAND_H"
                          [class]="si % 2 === 0 ? 'vitals-band-even' : 'vitals-band-odd'"/>
                }

                <!-- Vertical date guide lines (clipped per band) -->
                @for (s of chart().series; track s.label) {
                    @for (d of chart().dates; track d.x) {
                        <line [attr.x1]="d.x" [attr.y1]="s.bandY"
                              [attr.x2]="d.x" [attr.y2]="s.bandY + BAND_H"
                              class="vitals-grid-line"/>
                    }
                }

                <!-- Y-axis tick lines and labels per series -->
                @for (s of chart().series; track s.label) {
                    @for (t of s.yTicks; track t.value) {
                        <line [attr.x1]="ML" [attr.y1]="t.y"
                              [attr.x2]="ML + CHART_W" [attr.y2]="t.y"
                              class="vitals-ytick-line"/>
                        <text [attr.x]="ML - 5" [attr.y]="t.y"
                              class="vitals-ytick-label">{{ t.value }}</text>
                    }
                }

                <!-- Connecting line segments per series -->
                @for (s of chart().series; track s.label) {
                    <path [attr.d]="s.continuousPath"
                          fill="none" class="vitals-series-path"/>
                }

                <!-- Dots per series -->
                @for (s of chart().series; track s.label) {
                    @for (p of s.points; track $index) {
                        @if (p) {
                            <circle [attr.cx]="p.x" [attr.cy]="p.y" [attr.r]="DOT_R"
                                    class="vitals-dot">
                                <title>{{ p.display }}</title>
                            </circle>
                        }
                    }
                }

                <!-- Series labels (left axis, rotated 90°) -->
                @for (s of chart().series; track s.label) {
                    <text [attr.x]="10"
                          [attr.y]="s.bandY + BAND_H / 2"
                          [attr.transform]="'rotate(-90,10,' + (s.bandY + BAND_H / 2) + ')'"
                          class="vitals-series-label">{{ s.label }}</text>
                }

                <!-- X-axis date labels -->
                @for (d of chart().dates; track d.x) {
                    <text [attr.x]="d.x" [attr.y]="MT + chart().innerH + 16"
                          class="vitals-date-label">{{ d.label }}</text>
                }

                <!-- Full-height clickable zones per date column -->
                @for (z of chart().clickZones; track z.xi) {
                    <rect [attr.x]="z.x1" [attr.y]="MT"
                          [attr.width]="z.x2 - z.x1" [attr.height]="chart().innerH"
                          class="vitals-click-zone"
                          (click)="z.event && handleClick(z.event)"/>
                }

            </svg>
        } @else {
            <span style="font-size:0.85rem;opacity:0.6;font-style:italic">No vital measurements recorded</span>
        }
    `,
    imports: [CommonModule],
})
export class VitalsTimelineChartComponent {

    // Angular signals
    events      = input<Vitals[]>([]);
    onEventClick = input<(event: Vitals) => void>();

    // Expose constants to the template
    readonly ML      = ML;
    readonly MT      = MT;
    readonly BAND_H  = BAND_H;
    readonly CHART_W = CHART_W;
    readonly DOT_R   = DOT_R;

    readonly chart = computed((): ChartData => {
        const evts = [...this.events()].sort(
            (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
        );

        // Unique sorted date strings
        const uniqueDates = [...new Set(evts.map(e => e.date))];
        const nDates = uniqueDates.length;

        const xOf = (i: number): number =>
            nDates <= 1 ? ML + CHART_W / 2 : ML + (i / (nDates - 1)) * CHART_W;

        const dateObjs = uniqueDates.map((d, i) => ({ x: xOf(i), label: shortDate(d) }));

        // Only include series that have at least one non-null value
        const activeDefs = SERIES_DEFS.filter(def =>
            evts.some(e => (e as any)[def.key] != null),
        );

        const innerH = activeDefs.length * BAND_H + Math.max(0, activeDefs.length - 1) * BAND_GAP;
        const totalH = MT + innerH + MB;

        const series: ChartSeries[] = activeDefs.map((def, si) => {
            const bandY  = MT + si * (BAND_H + BAND_GAP);
            const yTop   = bandY + BAND_P;
            const yBot   = bandY + BAND_H - BAND_P;
            const [lo, hi] = def.range;

            // Two reference ticks: lo value (bottom) and hi value (top)
            const yTicks: YTick[] = [
                { y: yBot, value: String(lo) },
                { y: yTop, value: String(hi) },
            ];

            const points: (ChartPoint | null)[] = uniqueDates.map((d, xi) => {
                const evt = evts.find(e => e.date === d);
                const raw = evt ? (evt as any)[def.key] : null;
                if (!raw) return null;
                const norm = clampNorm(raw.value, def.range);
                return {
                    x: xOf(xi),
                    y: yBot - norm * (yBot - yTop),
                    event: evt!,
                    display: `${def.label}: ${raw.value} ${raw.unit}`,
                };
            });

            // Build a single continuous path, skipping null x-positions
            const available = points.filter((p): p is ChartPoint => p !== null);
            const continuousPath = available.length
                ? available.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')
                : '';

            return { label: def.label, bandY, points, continuousPath, yTicks };
        });

        // Vertical click zones — each column spans halfway to its neighbours
        const clickZones: ClickZone[] = uniqueDates.map((d, xi) => {
            const cx   = xOf(xi);
            const prev = xi > 0           ? xOf(xi - 1) : cx;
            const next = xi < nDates - 1  ? xOf(xi + 1) : cx;
            return {
                x1:    xi === 0           ? ML             : (prev + cx)   / 2,
                x2:    xi === nDates - 1  ? ML + CHART_W   : (cx   + next) / 2,
                xi,
                event: evts.find(e => e.date === d) ?? null,
            };
        });

        return {
            viewBox: `0 0 ${VB_W} ${totalH}`,
            totalH,
            innerH,
            dates: dateObjs,
            series,
            clickZones,
        };
    });

    handleClick(event: Vitals): void {
        this.onEventClick()?.(event);
    }
}
