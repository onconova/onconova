import { Pipe, PipeTransform } from "@angular/core"
import { User } from "../openapi"

@Pipe({
    standalone: true,
    name: 'acronym'
  })
export class GetNameAcronymPipe implements PipeTransform {
  
    transform(user: User): string {
        console.log(user)
        if (user.firstName && user.lastName) {
            return user.firstName[0].toUpperCase() + user.lastName[0].toUpperCase()
        } else {
            return user.username[0].toUpperCase() + user.username[1].toUpperCase()
        }
    }
}