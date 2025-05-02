import { Injectable } from '@angular/core';
import { CodedConcept, Measure, Period } from '../openapi';

@Injectable({
  providedIn: 'root'
})
export class TypeCheckService {

    public readonly isCodeableConcept = (value: CodedConcept): value is CodedConcept => !!value?.code;
    public readonly isRange = (value: Period): value is Period => value.hasOwnProperty('start') && value.hasOwnProperty('end');
    public readonly isPeriod = (value: Period): value is Period => value.hasOwnProperty('start') && value.hasOwnProperty('end') && (!isNaN(Date.parse(value?.end as string)) || isNaN(Date.parse(value?.start as string)) || Object.prototype.toString.call(value?.start) === '[object Date]');
    public readonly isMeasure = (value: Measure): value is Measure => !!value?.value && !!value?.unit;
    public readonly isObject = (x: any) => typeof x === 'object' && !Array.isArray(x) && x !== null
    public readonly isArray = (x: any) => x instanceof Array
    public readonly isDateString = (value: any): boolean => typeof value === 'string' && !isNaN(Date.parse(value)) && value.length === 10;
    public readonly isDate = (value: any): value is Date => Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime());
    public readonly isUUID = (value: any): boolean => /^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i.test(value);
}