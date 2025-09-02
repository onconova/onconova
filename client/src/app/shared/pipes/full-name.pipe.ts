
import { Pipe, PipeTransform } from "@angular/core"
import { User } from "onconova-api-client"

/**
 * Angular pipe to transform a `User` object into a full name string.
 *
 * This pipe returns the user's full name by concatenating the `firstName` (or `username` if `firstName` is not available)
 * and `lastName` properties. If the `lastName` is missing, only the `firstName` or `username` is returned.
 *
 * ```html
 * {{ user | fullname }}
 * ```
 *
 */
@Pipe({
    standalone: true,
    name: 'fullname'
  })
export class GetFullNamePipe implements PipeTransform {
  
    transform(user: User): string {
        if (!user) {
            return ''
        }
        const name = user.firstName || user.username
        const surname = user.lastName
        return surname ? name + ' ' + surname : name;
    }
}