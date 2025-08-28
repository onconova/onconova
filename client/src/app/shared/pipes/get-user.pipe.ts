import { inject, Pipe, PipeTransform } from "@angular/core"
import { User } from "onconova-api-client"
import { AuthService } from "src/app/core/auth/services/auth.service"
import { Observable } from "rxjs"

@Pipe({
    standalone: true,
    name: 'getUser'
  })
export class GetUserPipe implements PipeTransform {
    
    public authService = inject(AuthService)

    transform(username: string): Observable<User> {
        return this.authService.getUser(username)
    }
}