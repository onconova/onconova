import { Pipe, PipeTransform } from "@angular/core"
import { User } from "../openapi"

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