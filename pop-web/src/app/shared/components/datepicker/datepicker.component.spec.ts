import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DatePickerComponent } from './datepicker.component';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { DatePicker } from 'primeng/datepicker';
import { DateMaskDirective } from '../../directives/date-mask-directive';
import { formatDate } from '@angular/common';
import { By } from '@angular/platform-browser';

describe('DatePickerComponent', () => {
  let component: DatePickerComponent;
  let fixture: ComponentFixture<DatePickerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, FormsModule, CommonModule, DatePicker, DateMaskDirective],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DatePickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // Helper function to get the form control's value
  function getFormControlValue() {
    return component.formControl.value;
  }

  describe('writeValue', () => {
    it('should format single date correctly', () => {
      const isoDate = '2024-02-10'; // ISO date format
      component.writeValue(isoDate);
      expect(getFormControlValue()).toBe('10/02/2024');
    });

    it('should format date range correctly', () => {
      const dateRange = { start: '2023-02-01', end: '2023-12-31' };
      component.writeValue(dateRange);
      expect(getFormControlValue()).toBe('01/02/2023 - 31/12/2023');
    });

    it('should clear the value when input is null', () => {
      component.writeValue(null);
      expect(getFormControlValue()).toBeNull();
    });
  });
  describe('date formatting and parsing', () => {
    it('should correctly convert user input to ISO format', () => {
      const userInput = '10/02/2024'; // User-friendly format
      const expectedISO = '2024-02-10'; // ISO format

      const isoDate = component.parseToISO(userInput);
      expect(isoDate).toBe(expectedISO);
    });

    it('should correctly handle range input and output', () => {
      const userInputRange = '01/01/2023 - 31/12/2023'; // User-friendly range format
      const expectedISOStart = '2023-01-01';
      const expectedISOEnd = '2023-12-31';

      const parsedRange = userInputRange.split(' - ').map(date => component.parseToISO(date.trim()));
      expect(parsedRange[0]).toBe(expectedISOStart);
      expect(parsedRange[1]).toBe(expectedISOEnd);
    });
  });

  describe('UI Behavior', () => {
    it('should display the correct placeholder text', () => {
      const inputElement = fixture.debugElement.query(By.css('input'));
      expect(inputElement.nativeElement.placeholder).toBe('DD/MM/YYYY');
    });
  });
});
