import { Injectable } from '@angular/core'
import { Observable } from 'rxjs'
import { CancerPatientsService, NinjaPaginationResponseSchemaCancerPatientSchema } from '../openapi'

@Injectable({
  providedIn: 'root',
})
export class CancerPatientService {
  constructor(private api: CancerPatientsService) {}

  getCancerPatients(): Observable<NinjaPaginationResponseSchemaCancerPatientSchema> {
    return this.api.getCancerPatients()
  }
}