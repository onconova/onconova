import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControlErrorComponent, defaultErrors, FORM_ERRORS } from './form-control-error.component';
import { ReactiveFormsModule, FormGroup, FormControl, Validators, FormGroupDirective } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { BehaviorSubject } from 'rxjs';

describe('FormControlErrorComponent', () => {
    let component: FormControlErrorComponent;
    let fixture: ComponentFixture<FormControlErrorComponent>;
    let control: FormControl;
    let formGroup: FormGroup;
    let errors: any;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ReactiveFormsModule],
            providers: [
                FormGroupDirective,
                { provide: FORM_ERRORS, useValue: defaultErrors },
            ]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(FormControlErrorComponent);
        component = fixture.componentInstance;

        // Set up form and control
        control = new FormControl('', []);
        formGroup = new FormGroup({
            testControl: control
        });

        // Set the formGroupDirective mock
        const formGroupDirective = {
            control: formGroup,
            ngSubmit: new BehaviorSubject(null),
        };
        component.formGroupDirective = formGroupDirective as any; // Type cast to match actual implementation

        fixture.detectChanges();
    });

    it('should display required error message when control is empty and required', () => {
        control.setValidators([Validators.required]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control being touched or changed
        control.setValue('');
        fixture.detectChanges();

        // Check if the error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('This field is required.');
    });

    it('should display minlength error message when control value is too short', () => {
        control.setValidators([Validators.minLength(5)]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control value being too short
        control.setValue('abc');
        fixture.detectChanges();

        // Check if the error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('Minimum length is 5 characters.');
    });

    it('should display maxlength error message when control value is too long', () => {
        control.setValidators([Validators.maxLength(5)]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control value being too long
        control.setValue('abcdefgh');
        fixture.detectChanges();

        // Check if the error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('Maximum length is 5 characters.');
    });

    it('should display email error message when control value is not a valid email', () => {
        control.setValidators([Validators.email]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control value being an invalid email
        control.setValue('invalid-email');
        fixture.detectChanges();

        // Check if the error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('Please enter a valid email address.');
    });

    it('should display min error message when control value is below the minimum', () => {
        control.setValidators([Validators.min(5)]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control value being below the minimum
        control.setValue(3);
        fixture.detectChanges();

        // Check if the error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('Value must be greater than or equal to 5.');
    });

    it('should display custom error message from customErrors object', () => {
        // Define custom error messages
        const customErrors = {
            required: 'This field cannot be empty.',
            pattern: 'Invalid pattern!',
        };

        component.customErrors = customErrors;

        control.setValidators([Validators.required]);
        control.updateValueAndValidity();
        fixture.detectChanges();

        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Simulate control being empty
        control.setValue('');
        fixture.detectChanges();

        // Check if the custom error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage.nativeElement.textContent).toBe('This field cannot be empty.');
    });


    it('should display no error when there are no errors on the control', () => {
        // Set the component inputs
        component.controlName = 'testControl';
        component.ngOnInit();

        // Set control to valid value
        control.setValue('validValue');
        fixture.detectChanges();

        // Check that no error message is displayed
        const errorMessage = fixture.debugElement.query(By.css('.text-danger'));
        expect(errorMessage).toBeNull();
    });
});
