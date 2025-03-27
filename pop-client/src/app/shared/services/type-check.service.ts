import { Injectable } from '@angular/core';

import JSZip from 'jszip';
import { CodedConcept, Measure, Period } from '../openapi';

@Injectable({
  providedIn: 'root'
})
export class TypeCheckService {

    public readonly isCodeableConcept = (value: CodedConcept): value is CodedConcept => !!value?.code;
    public readonly isPeriod = (value: Period): value is Period => !!value?.start;
    public readonly isMeasure = (value: Measure): value is Measure => !!value?.value;
    public readonly isObject = (x: any) => typeof x === 'object' && !Array.isArray(x) && x !== null
    public readonly isArray = (x: any) => x instanceof Array
    public readonly isDateString = (value: any): boolean => typeof value === 'string' && !isNaN(Date.parse(value));
    public readonly isDate = (value: any): value is Date => Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime());

}