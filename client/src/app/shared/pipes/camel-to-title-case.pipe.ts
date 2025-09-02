
import { Pipe, PipeTransform } from '@angular/core';

/**
 * Angular pipe that transforms a camelCase string into Title Case format.
 *
 * This pipe inserts spaces between camelCase words and capitalizes the first letter of each word.
 *
 * ```html
 * {{ 'camelCaseString' | camelCaseToTitleCase }}
 * ```
 * 
 * - If the input string is already in Title Case or contains spaces, it will capitalize the first letter of each word.
 * - Non-alphabetic characters are preserved.
 *
 */
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
