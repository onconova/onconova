import { Injectable } from '@angular/core'
import { Observable } from 'rxjs'
import { DefaultService, CancerPatientOut } from '../openapi'

@Injectable({
  providedIn: 'root',
})
export class CancerPatientService {
  constructor(private api: DefaultService) {}

  getCancerPatients(): Observable<CancerPatientOut[]> {
    return this.api.popCoreApiGetAllCancerPatientMatchingTheQuery()
  }
}