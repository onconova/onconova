import { inject, Injectable} from '@angular/core';
import { AuthService, User } from '../../openapi';
import { map, Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class UserBadgeService {

    private readonly userService: AuthService = inject(AuthService);
    private cache = new Map<string, User>();

    getUser(username: string): Observable<User> {
        const cachedUser = this.cache.get(username) 
        if (!cachedUser) {
            return this.userService.getUsers({username: username, limit: 1}).pipe(
                map(response => {
                    let user = response.items[0]
                    this.cache.set(username, user)
                    return user
                })
            )
        }
        return of(cachedUser)
    }

}