import { inject, Input, Component, OnInit, OnDestroy, ChangeDetectionStrategy} from '@angular/core';
import { NgIf } from '@angular/common';
import { InjectionToken } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { ValidationErrors, FormGroupDirective, AbstractControl, FormGroupName, ControlContainer } from '@angular/forms';
import { BehaviorSubject, Subscription, distinctUntilChanged, merge } from 'rxjs';

export const defaultErrors = {
  required: () => `This field is required.`,
  pattern: () => `This field has an invalid format.`,
  minlength: (err: {requiredLength: number, actualLength: number}) => `Minimum length is ${err.requiredLength} characters.`,
  maxlength: (err: {requiredLength: number, actualLength: number}) => `Maximum length is ${err.requiredLength} characters.`,
  email: () => `Please enter a valid email address.`,
  min: (err: {min: number, actual: number}) => `Value must be greater than or equal to ${err.min}.`,
  max: (err: {max: number, actual: number}) => `Value must be less than or equal to ${err.max}.`,
  // Adding custom error messages for some common validation checks
  validateDate: () => `Please enter a valid date.`,
  validateNumber: () => `Please enter a valid number.`,
  validatePhone: () => `Please enter a valid phone number.`,
  validateZip: () => `Please enter a valid ZIP code.`,
};

export const FORM_ERRORS = new InjectionToken('FORM_ERRORS', {
  providedIn: 'root',
  factory: () => defaultErrors
});

@Component({
    selector: 'pop-form-control-error',
    imports: [AsyncPipe],
    template: `
      @let message = message$ | async;
      @if (message) {
        <div class="text-danger mt-2" style="color:#e24c4c">{{ message }}</div>
      }
    `,
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FormControlErrorComponent implements OnInit, OnDestroy {

  @Input({required: true}) controlName!: string;
  @Input() customErrors?: ValidationErrors;

  public controlContainer = inject(ControlContainer);
  private subscription = new Subscription();
  private errors: any = inject(FORM_ERRORS);
  public message$ = new BehaviorSubject<string>('');

  ngOnInit(): void {
    // Initialize the control error handling
    this.initializeControlErrorHandling();
  }

  private initializeControlErrorHandling() {
    // Check if the controlName is provided and the form group directive is available
    if (this.controlContainer && this.controlName) {
        // Get the control from the form group directive
        const control = this.controlContainer.control?.get(this.controlName);

        if (control) {
            // Subscribe to the control's errors and the form group directive's ngSubmit event
            this.subscribeToControlErrors(control);
        } else {
            console.error(`Control "${this.controlName}" not found in the form group.`);
        }
    } else {
        console.error('FormControlErrorComponent must be used within a FormGroupDirective and "controlName" must be provided.');
    }
  }


  private subscribeToControlErrors(control: AbstractControl) {
    this.subscription.unsubscribe();
    const formSubmit$ = 'ngSubmit' in this.controlContainer ? (this.controlContainer as any).ngSubmit : [];

    this.subscription = merge(control.valueChanges, formSubmit$)
      .pipe(distinctUntilChanged())
      .subscribe(() => {
        const controlErrors = control.errors;
        const errorMessage = this.getErrorMessage(controlErrors);
        this.setError(errorMessage);
      });
  }

  private getErrorMessage(errors: ValidationErrors | null): string {
    if (!errors) {
        // Return an empty string if there are no errors
        return '';
    }

    // Get the first error key
    const firstErrorKey = Object.keys(errors)[0];

    // Get the error message from the custom error messages if provided, otherwise use the default error message
    const getError = this.errors[firstErrorKey];

    // Get the custom error message if provided, otherwise default error message
    const errorText = this.customErrors?.[firstErrorKey] || getError(errors[firstErrorKey]);
    return errorText;
  }


  private setError(message: string): void {
    this.message$.next(message);
  }

  ngOnDestroy(): void {
    // Clean up the subscription
    this.subscription.unsubscribe();
  }
}
