import { Injectable } from '@angular/core'
import { Observable } from 'rxjs'
import { PatientCasesService, NinjaPaginationResponseSchemaPatientCaseSchema } from '../core/modules/openapi'

@Injectable({
  providedIn: 'root',
})
export class PatientCaseService {
  constructor(private api: PatientCasesService) {}

  getPatientCases(): Observable<NinjaPaginationResponseSchemaPatientCaseSchema> {
    return this.api.getPatientCases()
  }
}