import { Component, Input, ViewEncapsulation } from '@angular/core';
import { InlineSVGModule } from 'ng-inline-svg-2';

@Component({
    standalone: true,
    selector: 'cancer-icon',
    styleUrl: 'cancer-icon.component.css',
    encapsulation: ViewEncapsulation.None,
    template:`
    <div [inlineSVG]="icon" class="cancer-icon">
    </div>
    `,
    imports: [
        InlineSVGModule,
    ]
})
export class CancerIconComponent {

    @Input() topography!: string;
    public icon : string = 'assets/images/body/symptom.svg';
    private icons = {
        'mouth.svg': ['C00', 'C01', 'C02', 'C03', 'C04', 'C06'],
        'head.svg': ['C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14',],
        'stomach.svg': ['C16'],
        'intestine.svg': ['C17'],
        'colon.svg': ['C18', 'C19', 'C20',],
        'anus.svg': ['C21', 'C48'],
        'liver.svg': ['C22',],
        'ballbladder.svg': ['C23',],
        'pancreas.svg': ['C25',],
        'lungs.svg': ['C37', 'C33', 'C34', 'C39'],
        'ears_nose_and_throat.svg': ['C30', 'C31', 'C32'],
        'heart_organ.svg': ['C38',],
        'joints.svg': ['C40', 'C41'],
        'blood_cells.svg': ['C42'],
        'arm.svg': ['C44'],
        'nerve.svg': ['C47','C72'],
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


    ngOnInit() {
        console.log(this.topography)
        Object.entries(this.icons).forEach(
            icon => {
                const topographies = icon[1];
                if (topographies.includes(this.topography.split('.')[0])) {
                    this.icon = `assets/images/body/${icon[0]}`
                    return
                }
            }
        )
    }

}