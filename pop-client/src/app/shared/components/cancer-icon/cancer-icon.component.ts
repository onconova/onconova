import { Component, computed, input, signal } from '@angular/core';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { Skeleton } from 'primeng/skeleton';

@Component({
    selector: 'pop-cancer-icon',
    template: `
    <div [inlineSVG]="icon()" 
        class="pop-cancer-icon" 
        [setSVGAttributes]="{style: 'margin: auto; display: block;', height: height(), width: width()}"
        (onSVGInserted)="loadingSVG.set(false)" 
        style="display: {{loadingSVG() ? 'none' : 'block'}}">
    </div>
    @if (loadingSVG()) {
        <p-skeleton [height]="height()" [width]="width()"/>
    }
    `,
    imports: [
        InlineSVGModule, Skeleton
    ]
})
export class CancerIconComponent {

    // Component inputs
    public topography = input.required<string>();
    public height = input<string>('2rem');
    public width = input<string>('2rem');

    readonly #defaultIcon : string = 'assets/images/body/unknown.svg';
    readonly #icons = {
        'mouth.svg': ['C00', 'C01', 'C02', 'C03', 'C04', 'C06'],
        'head.svg': ['C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14',],
        'stomach.svg': ['C16'],
        'intestine.svg': ['C17'],
        'colon.svg': ['C18', 'C19', 'C20',],
        'anus.svg': ['C21', 'C48'],
        'liver.svg': ['C22',],
        'gallbladder.svg': ['C23',],
        'pancreas.svg': ['C25',],
        'lungs.svg': ['C37', 'C33', 'C34', 'C39'],
        'ears_nose_and_throat.svg': ['C30', 'C31', 'C32'],
        'heart_organ.svg': ['C38',],
        'joints.svg': ['C40', 'C41'],
        'blood_cells.svg': ['C42'],
        'skin_cancer.svg': ['C44'],
        'oesophagus_cancer.svg': ['C15'],
        'nerve.svg': ['C47','C72', 'C49'],
        'breasts.svg': ['C50'],
        'vulva.svg': ['C51'],
        'vagina.svg': ['C52'],
        'cervical_cancer.svg': ['C53'],
        'female_reproductive_system.svg': ['C54', 'C55', 'C56', 'C57'],
        'fetus.svg': ['C58',],
        'penis.svg': ['C60',],
        'prostate.svg': ['C61',],
        'testicles.svg': ['C62','C63'],
        'kidneys.svg': ['C64','C65','C66'],
        'bladder.svg': ['C67', 'C68'],
        'eye.svg': ['C69'],
        'brain.svg': ['C70','C71'],
        'thyroid.svg': ['C73'],
        'endocrinology.svg': ['C74','C75'],
        'lymph_nodes.svg': ['C77'],
    }

    public loadingSVG = signal<boolean>(true);
    public icon = computed(() => {
        if (!this.topography()) {
            return this.#defaultIcon
        } 
        let icon = Object.entries(this.#icons).find(
            ([filename, topographies]) => topographies.includes(this.topography().split('.')[0])
        )       
        if (!icon) {
            return this.#defaultIcon
        }                 
        return `assets/images/body/${icon[0]}`
    });

}