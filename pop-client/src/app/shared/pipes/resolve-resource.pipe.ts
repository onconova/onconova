import { inject, Pipe, PipeTransform } from "@angular/core"
import { InteroperabilityService } from "pop-api-client";
import { Observable } from "rxjs";

@Pipe({     
    standalone: true,
    name: 'resolve' 
})
export class ResolveResourcePipe implements PipeTransform {

    private readonly interoperabilityService = inject(InteroperabilityService)

    transform(value: string): Observable<string> {    
      return this.interoperabilityService.resolveResourceId({resourceId: value});
    }
}
