import { Component, inject, Input, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { PatientCaseBundle } from 'src/app/shared/openapi';

import { TreeNode } from 'primeng/api';
import { TabsModule } from 'primeng/tabs';
import { SelectButtonModule } from 'primeng/selectbutton';
import { StepperModule } from 'primeng/stepper';

import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { TreeModule } from 'primeng/tree';
import { AvatarModule } from 'primeng/avatar';
import { Divider } from 'primeng/divider';
import { AuthService } from 'src/app/core/auth/services/auth.service';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { Badge } from 'primeng/badge';
import { ModalFormComponent } from "../../../../../shared/components/identicon/identicon.component";

@Component({
    standalone: true,
    selector: 'pop-case-importer-bundle-viewer',
    templateUrl: 'case-importer-bundle-viewer.component.html',
    styles: `
        .illustration {
        color: var(--p-primary-color);
        display: flex;   
        height: 15rem;
        }
    `,
    imports: [
    CommonModule,
    FormsModule,
    NgxJsonViewerModule,
    InlineSVGModule,
    AvatarModule,
    Badge,
    Divider,
    SelectButtonModule,
    StepperModule,
    TabsModule,
    TreeModule,
    ModalFormComponent
],
})
export class CaseImporterBundleViewerComponent {
    @Input({required: true}) bundle!: PatientCaseBundle;
    public readonly authService: AuthService = inject(AuthService);
    public bundleTreeNodes: TreeNode[] = [];

    ngOnChanges(changes: SimpleChanges) {
        if (changes['bundle'] && this.bundle) {
            this.bundleTreeNodes = this.constructBundleTree(this.bundle);
        }
    }

    ngOnInit() {
        this.bundleTreeNodes = this.constructBundleTree(this.bundle);
    }

    private constructBundleTree(bundle: PatientCaseBundle): TreeNode[] {
        return Object.entries(bundle)
            .filter(([key,value]) => Array.isArray(value) && key!='updatedBy') // Only process array properties
            .map(([key,value]) => ({
                label: key
                    .replace(/([a-z])([A-Z])/g, '$1 $2')
                    .replace(/^./, (str) => str.toUpperCase()),
                type: 'category',
                children: value.map((item: any) => ({
                    label: item.description,
                    type: 'resource',
                    data: item,
                })),
            }));
    }
}