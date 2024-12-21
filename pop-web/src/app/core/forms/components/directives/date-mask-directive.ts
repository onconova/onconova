import { AfterViewInit, Directive, ElementRef  } from '@angular/core';
import { NgControl } from '@angular/forms';

import { DatePicker } from 'primeng/datepicker';
import Inputmask from "inputmask";

@Directive({
  standalone: true,
  selector: '[dateMask]'
})
export class DateMaskDirective implements AfterViewInit {
  constructor(
    private primeCalendar: DatePicker, 
    private ngControl: NgControl,  
    private elementRef: ElementRef
  ) { }
  
  private inputElement!: HTMLInputElement;

  ngAfterViewInit() {
    this.inputElement = this.elementRef.nativeElement.querySelector('input');
    new Inputmask( this.getDateMask(), {placeholder: this.getPlaceholder()} ).mask(this.inputElement);
    // Update the form control value when the input value changes
    this.inputElement.addEventListener('input', () => {
      if (this.inputElement.inputmask?.isComplete()){
        this.ngControl.control?.setValue(this.inputElement.value);  
      }
    });
  }
  getPlaceholder(): string {
    let date_placeholder
    if (this.primeCalendar.view == 'date') {
      date_placeholder =  '__/__/____';
    } else if (this.primeCalendar.view == 'month') {
      date_placeholder = '__/____';
    } else if (this.primeCalendar.view == 'year') {
      date_placeholder = '____';
    } else {
      date_placeholder = '__/__/____ __:__'
    }
    if (this.primeCalendar.selectionMode == 'single') {
      return date_placeholder
    } else if (this.primeCalendar.selectionMode == 'range') {
      return `${date_placeholder} - ${date_placeholder}`
    } else {
      return date_placeholder
    }
  }

  getDateMask(): string {
    let date_mask
    if (this.primeCalendar.view == 'date') {
      date_mask = '99/99/9999';
    } else if (this.primeCalendar.view == 'month') {
      date_mask = '99/9999';
    } else if (this.primeCalendar.view == 'year') {
      date_mask = '9999';
    } else {
      date_mask = '99/99/9999 99:99'
    }
    if (this.primeCalendar.selectionMode == 'single') {
      return date_mask
    } else if (this.primeCalendar.selectionMode == 'range') {
      return `${date_mask} - ${date_mask}`
    } else {
      return date_mask
    }
  }
}