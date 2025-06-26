import { inject, Pipe, PipeTransform } from "@angular/core"
import { InteroperabilityService } from "pop-api-client";
import { catchError, map, Observable, of } from "rxjs";

@Pipe({     
    standalone: true,
    name: 'resolve' 
})
export class ResolveResourcePipe implements PipeTransform {

  private readonly interoperabilityService = inject(InteroperabilityService)

  transform(value: string): Observable<string> {    
    return this.interoperabilityService.resolveResourceId({resourceId: value}).pipe(
      catchError(error => {
        if (error.status === 404) {
          return of('Deleted resource');
        } else {
          // rethrow or handle other errors as needed
          throw error;
        }
      })
    );
  }
}
