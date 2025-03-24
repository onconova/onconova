
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    standalone: true,
    name: 'camelCaseToTitleCase'
})
export class CamelCaseToTitleCasePipe implements PipeTransform {
    transform(value: string): string {
        return value
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
}
