import { AfterViewInit, Directive } from '@angular/core';
import { Calendar } from 'primeng/calendar';
import Inputmask from "inputmask";

@Directive({
  selector: '[dateMask]'
})
export class DateMaskDirective implements AfterViewInit {
  constructor(private primeCalendar: Calendar) { }

  ngAfterViewInit() {
    new Inputmask( this.getDateMask(), {placeholder: '__/__/____'} ).mask( this.getHTMLInput());
  }

  getHTMLInput(): HTMLInputElement {
    return this.primeCalendar.el.nativeElement.querySelector('input');
  }

  getDateMask(): string {
    if(this.primeCalendar.timeOnly) {
      return '99:99';
    } else if(this.primeCalendar.showTime) {
      return '99/99/9999 99:99';
    } else {
      return '99/99/9999';
    }
  }
}