import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { PatientListComponent } from './patient-list.component';

@NgModule({
    imports: [RouterModule.forChild([
        { path: '', component: PatientListComponent }
    ])],
    exports: [RouterModule]
})
export class PatientListRoutingModule { }
