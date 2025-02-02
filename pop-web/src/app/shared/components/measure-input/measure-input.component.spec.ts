import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MeasureInputComponent } from './measure-input.component';
import { HttpClient, HttpHandler } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MeasuresService } from 'src/app/shared/openapi';
import { of } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';

// Mock service
class MockMeasuresService {
  getMeasureUnits() {
    return of(['kg', 'lb', 'g']); // Mocked response for allowed units
  }
  
  getMeasureDefaultUnits() {
    return of('kg'); // Mocked response for the default unit
  }
}

describe('MeasureInputComponent', () => {
  let component: MeasureInputComponent;
  let fixture: ComponentFixture<MeasureInputComponent>;
  let measuresService: MeasuresService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, FormsModule, InputNumber, Select],
      providers: [
        { provide: MeasuresService, useClass: MockMeasuresService }
      ],
      schemas: [NO_ERRORS_SCHEMA] // Ignores unrecognized elements, e.g. third-party library components
    })
    .compileComponents();

    fixture = TestBed.createComponent(MeasureInputComponent);
    component = fixture.componentInstance;
    component.measure = 'mockMeasure';
    measuresService = TestBed.inject(MeasuresService);

    fixture.detectChanges(); // Trigger initial data binding
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default unit and allowed units', () => {
    // Check the default unit
    component.defaultUnit$.subscribe((unit) => {
      expect(unit.unit).toBe('kg');
      expect(unit.display).toBe('kg');
    });

    // Check the allowed units
    component.allowedUnits$.subscribe((units) => {
      expect(units.length).toBeGreaterThan(0);
      expect(units).toEqual([
        { unit: 'kg', display: 'kg' },
        { unit: 'lb', display: 'lb' },
        { unit: 'g', display: 'g' }
      ]);
    });
  });

  it('should update the form control value when input value and unit are set', () => {
    // Set input value and unit
    component.inputValue = 10;
    component.selectedUnit = { unit: 'kg', display: 'kg' };

    spyOn(component.formControl, 'setValue'); // Spy on setValue method

    // Trigger update
    component.updateFormControlValue();

    // Check that setValue was called with the correct values
    expect(component.formControl.setValue).toHaveBeenCalledWith({
      value: 10,
      unit: 'kg'
    });
  });

  it('should handle null values correctly', () => {
    component.inputValue = null;
    component.selectedUnit = { unit: 'kg', display: 'kg' };

    spyOn(component.formControl, 'setValue');

    component.updateFormControlValue();
    
    expect(component.formControl.setValue).toHaveBeenCalledWith(null);
  });

  it('should call registerOnChange and registerOnTouched when subscribing to valueChanges', () => {
    const mockFn = jasmine.createSpy('mockFn');
    component.registerOnChange(mockFn);
    component.registerOnTouched(mockFn);

    // Trigger form control value change
    component.formControl.setValue({ value: 20, unit: 'g' });

    // Verify that both change and touched callbacks are triggered
    expect(mockFn).toHaveBeenCalledTimes(2);
  });

  it('should write value to the component correctly', () => {
    const value = { value: 100, unit: 'lb' };

    component.writeValue(value);

    expect(component.inputValue).toBe(100);
    expect(component.selectedUnit.unit).toBe('lb');
    expect(component.formControl.value).toEqual(value);
  });
});
