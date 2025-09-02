import { Injectable } from '@angular/core';
import { CodedConcept, Measure, Period, Range } from 'onconova-api-client';

/**
 * Service providing type-checking utility methods for various domain-specific and primitive types.
 *
 * This service is intended to be injected wherever type validation is required, such as in form validation,
 * API response handling, or data transformation logic. It includes methods to check for specific types
 * like `CodedConcept`, `Range`, `Period`, `Measure`, as well as general utilities for arrays, objects,
 * dates, booleans, UUIDs, and date strings.
 *
 * ```typescript
 * private typeCheck = inject(TypeCheckService);
 *
 * const concept = { code: '123' };
 * if (this.typeCheck.isCodeableConcept(concept)) {
 *   // concept is a valid CodedConcept
 * }
 *
 * const dateStr = '2024-06-01';
 * if (this.typeCheck.isDateString(dateStr)) {
 *   // dateStr is a valid date string in YYYY-MM-DD format
 * }
 * ```
 *
 * - The type guards for domain-specific types (`CodedConcept`, `Range`, `Period`, `Measure`) assume minimal shape validation.
 * - `isDateString` checks for a string of length 10 that parses as a date, typically in `YYYY-MM-DD` format.
 * - `isUUID` validates against RFC 4122 version 4 UUIDs.
 */
@Injectable({
  providedIn: 'root'
})
export class TypeCheckService {

    public readonly isCodeableConcept = (value: CodedConcept): value is CodedConcept => !!value?.code;
    public readonly isRange = (value: Range): value is Range => value.hasOwnProperty('start') && value.hasOwnProperty('end') && typeof value.start === 'number' && typeof value.end === 'number';;
    public readonly isPeriod = (value: Period): value is Period => value.hasOwnProperty('start') && value.hasOwnProperty('end') && (!isNaN(Date.parse(value?.end as string)) || !isNaN(Date.parse(value?.start as string)) || Object.prototype.toString.call(value?.start) === '[object Date]');
    public readonly isMeasure = (value: Measure): value is Measure => !!value?.value && !!value?.unit;
    public readonly isObject = (x: any) => typeof x === 'object' && !Array.isArray(x) && x !== null
    public readonly isArray = (x: any) => x instanceof Array
    public readonly isDateString = (value: any): boolean => typeof value === 'string' && !isNaN(Date.parse(value)) && value.length === 10;
    public readonly isBoolean = (value: any): boolean => typeof value === 'boolean';
    public readonly isDate = (value: any): value is Date => Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime());
    public readonly isUUID = (value: any): boolean => /^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i.test(value);
}