import { AfterViewInit, Directive, ElementRef  } from '@angular/core';
import { NgControl } from '@angular/forms';

import { Calendar } from 'primeng/calendar';
import Inputmask from "inputmask";

@Directive({
  selector: '[dateMask]'
})
export class DateMaskDirective implements AfterViewInit {
  constructor(
    private primeCalendar: Calendar, 
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
    if (this.primeCalendar.view == 'date') {
      return '__/__/____';
    } else if (this.primeCalendar.view == 'month') {
      return '__/____';
    } else if (this.primeCalendar.view == 'year') {
      return '____';
    } else {
      return '__/__/____ __:__'
    }
  }

  getDateMask(): string {
    if (this.primeCalendar.view == 'date') {
      return '99/99/9999';
    } else if (this.primeCalendar.view == 'month') {
      return '99/9999';
    } else if (this.primeCalendar.view == 'year') {
      return '9999';
    } else {
      return '99/99/9999 99:99'
    }
  }
}