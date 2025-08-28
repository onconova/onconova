import { AfterViewInit, Directive, ElementRef } from '@angular/core';
import { NgControl } from '@angular/forms';
import { DatePicker } from 'primeng/datepicker';
import IMask from 'imask';

@Directive({
  standalone: true,
  selector: '[dateMask]'
})
export class DateMaskDirective implements AfterViewInit {
  constructor(
    private primeCalendar: DatePicker,
    private ngControl: NgControl,
    private elementRef: ElementRef
  ) {}

  private inputElement!: HTMLInputElement;
  private maskRef?: ReturnType<typeof IMask>;

  ngAfterViewInit(): void {
    this.inputElement = this.elementRef.nativeElement.querySelector('input');

    this.maskRef = IMask(this.inputElement, {
      mask: this.getIMaskPattern(),
      placeholderChar: '_'
    });

    this.inputElement.placeholder = this.getPlaceholder();

    this.inputElement.addEventListener('input', () => {
      if (this.maskRef?.masked?.isComplete) {
        this.ngControl.control?.setValue(this.inputElement.value);
      }
    });
  }

  private getIMaskPattern(): string {
    let pattern: string;
    if (this.primeCalendar.view === 'date') {
      pattern = '00/00/0000';
    } else if (this.primeCalendar.view === 'month') {
      pattern = '00/0000';
    } else if (this.primeCalendar.view === 'year') {
      pattern = '0000';
    } else {
      pattern = '00/00/0000 00:00';
    }

    if (this.primeCalendar.selectionMode === 'range') {
      return `${pattern} - ${pattern}`;
    }

    return pattern;
  }

  private getPlaceholder(): string {
    let placeholder: string;
    if (this.primeCalendar.view === 'date') {
      placeholder = '__/__/____';
    } else if (this.primeCalendar.view === 'month') {
      placeholder = '__/____';
    } else if (this.primeCalendar.view === 'year') {
      placeholder = '____';
    } else {
      placeholder = '__/__/____ __:__';
    }

    if (this.primeCalendar.selectionMode === 'range') {
      return `${placeholder} - ${placeholder}`;
    }

    return placeholder;
  }
}