import { Injectable } from '@angular/core'
import { Observable } from 'rxjs'
import { PatientCasesService, PaginatedPatientCase } from '../core/modules/openapi'
import { NeoplasticEntitiesService, PaginatedNeoplasticEntity } from '../core/modules/openapi'

@Injectable({
  providedIn: 'root',
})
export class PatientCaseService {
  constructor(
    private api: PatientCasesService,
    private neoplasticEntitiesService: NeoplasticEntitiesService
  ) {}

  getPatientCases(): Observable<PaginatedPatientCase> {
    return this.api.getPatientCases()
  }

  getFilteredPatientCases(ageLte: number, ageGte: number): Observable<PaginatedPatientCase> {
    let pseudoidentifier = undefined; 
    let deceased = undefined; 
    let boolean = undefined; 
    let gender = undefined; 
    return this.api.getPatientCases(ageLte, ageGte, pseudoidentifier, deceased, boolean, gender)
  }

}