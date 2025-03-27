import { inject, Input, Component, OnInit, OnDestroy, ChangeDetectionStrategy} from '@angular/core';
import { NgIf } from '@angular/common';
import { InjectionToken } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { ValidationErrors, FormGroupDirective, AbstractControl } from '@angular/forms';
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
    standalone: true,
    selector: 'pop-form-control-error',
    imports: [AsyncPipe],
    template: `
      @let message = message$ | async;
      @if (message) {
        <div class="text-danger mt-2" style="color:#e24c4c">{{ message }}</div>
      }
    `,
    changeDetection: ChangeDetectionStrategy.OnPush,
  })
export class FormControlErrorComponent implements OnInit, OnDestroy {

  /**
   * The name of the control in the form group to display the errors for.
   */
  @Input({required: true}) controlName!: string;

  /**
   * Custom error messages to use for the control. If provided, will override the default error messages.
   */
  @Input() customErrors?: ValidationErrors;

  /**
   * The form group directive this component is used within.
   */
  public formGroupDirective = inject(FormGroupDirective);

  /**
   * Subscription to the form group directive's ngSubmit event and the control's value changes.
   */
  private subscription = new Subscription();

  /**
   * The default error messages to use if custom error messages are not provided.
   */
  private errors: any = inject(FORM_ERRORS);

  /**
   * The error message to display. Will be an empty string if there are no errors.
   */
  public message$ = new BehaviorSubject<string>('');

  ngOnInit(): void {
    // Initialize the control error handling
    this.initializeControlErrorHandling();
  }

  /**
   * Initialize the control error handling.
   */
  private initializeControlErrorHandling() {
    // Check if the controlName is provided and the form group directive is available
    if (this.formGroupDirective && this.controlName) {
        // Get the control from the form group directive
        const control = this.formGroupDirective.control.get(this.controlName);

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

  /**
   * Subscribe to the control's errors and the form group directive's ngSubmit event.
   * @param control The control to subscribe to
   */
  private subscribeToControlErrors(control: AbstractControl) {
    // Unsubscribe from any previous subscriptions to avoid memory leaks
    this.subscription.unsubscribe();
    
    // Subscribe to the control's value changes and the form group directive's ngSubmit event
    this.subscription = merge(control.valueChanges, this.formGroupDirective.ngSubmit)
        .pipe(distinctUntilChanged())
        .subscribe(() => {
            // Get the control errors
            const controlErrors = control.errors;

            // Get the error message
            const errorMessage = this.getErrorMessage(controlErrors);

            // Set the error message
            this.setError(errorMessage);
        });
  }

  /**
   * Get the error message for the control errors.
   * @param errors The control errors
   */
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

  /**
   * Set the error message to display.
   * @param message The error message to display
   */
  private setError(message: string): void {
    this.message$.next(message);
  }

  ngOnDestroy(): void {
    // Clean up the subscription
    this.subscription.unsubscribe();
  }
}
