import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, Router } from '@angular/router';
import { Observable, EMPTY } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { PatientCaseIdentifier, PatientCasesService } from 'pop-api-client';

@Injectable({ providedIn: 'root' })
export class CaseResolver implements Resolve<any> {
  constructor(private caseService: PatientCasesService, private router: Router) {}

  resolve(route: ActivatedRouteSnapshot): Observable<any> {
    const pseudoidentifier = route.paramMap.get('pseudoidentifier') as string;
    return this.caseService.getPatientCaseById({caseId: pseudoidentifier, type: PatientCaseIdentifier.Pseudoidentifier}).pipe(
      catchError(error => {
        if (error.status === 404) {
          // Redirect to a 404 page (make sure you have a route for this)
          this.router.navigate(['/notfound']);
        }
        return EMPTY;
      }),
      map(response => response.id)
    );
  }
}