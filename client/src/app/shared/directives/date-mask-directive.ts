import { AfterViewInit, Directive, ElementRef } from '@angular/core';
import { NgControl } from '@angular/forms';
import { DatePicker } from 'primeng/datepicker';
import IMask from 'imask';

/**
 * 
 * Applies an input mask to date fields using IMask, tailored for PrimeNG DatePicker components.
 * The mask pattern and placeholder are dynamically set based on the DatePicker's view and selection mode.
 * Supports masking for date, month, year, and datetime formats, as well as range selection.
 *
 * - This directive is intended to be used with PrimeNG's DatePicker component.
 * - The mask adapts automatically to the DatePicker's `view` (`date`, `month`, `year`, or other) and `selectionMode` (`single` or `range`).
 * - The directive updates the form control value only when the input is complete according to the mask.
 * - Ensure that the directive is applied to a PrimeNG DatePicker element for correct behavior.
 * 
 * ```html
 * <p-calendar dateMask [(ngModel)]="date"></p-calendar>
 * ```
 * 
 */
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