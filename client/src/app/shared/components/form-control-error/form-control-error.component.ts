/**
 * Displays validation error messages for a specific form control within a form group.
 *
 * This component listens to validation errors on a given form control and displays the corresponding error message.
 * It supports both default and custom error messages, and updates the displayed message on value changes or form submission.
 *
 * - This component must be used inside a form group directive (e.g., within a `<form [formGroup]>`).
 * - The `controlName` input is required and should match the name of the control in the parent form group.
 * - Custom error messages can be provided via the `customErrors` input; otherwise, default messages are used.
 * - Error messages are shown only when the control has validation errors.
 *
 * ```html
 * <form [formGroup]="myForm" (ngSubmit)="onSubmit()">
 *   <input formControlName="email" />
 *   <onconova-form-control-error [controlName]="'email'"></onconova-form-control-error>
 * </form>
 * ```
 *
 * ```html
 * <!-- Providing custom error messages: -->
 * <onconova-form-control-error
 *   [controlName]="'phone'"
 *   [customErrors]="{ required: 'Phone number is required!', pattern: 'Invalid phone format.' }">
 * </onconova-form-control-error>
 * ```
 */
import { inject, Component, OnDestroy, input, signal, effect} from '@angular/core';
import { InjectionToken } from '@angular/core';
import { ValidationErrors, AbstractControl, ControlContainer } from '@angular/forms';
import { Message } from 'primeng/message';
import { Subscription, distinctUntilChanged, merge } from 'rxjs';

export const DEFAULT_ERRORS = {
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
  factory: () => DEFAULT_ERRORS
});



@Component({
    selector: 'onconova-form-control-error',
    imports: [Message],
    template: `
      @if (message()) {
        <p-message class="mt-2" severity="error">{{ message() }}</p-message>
      }
    `,
})
export class FormControlErrorComponent implements OnDestroy {

  // Component inputs
  public controlName = input.required<string>()
  public customErrors = input<ValidationErrors>()

  // Component injections
  readonly #controlContainer = inject(ControlContainer);
  readonly #errors: any = inject(FORM_ERRORS);
  
  #subscription = new Subscription();
  public message = signal<string | null>(null);


  #initializeControlErrorHandling = effect(() => {
    // Check if the controlName is provided and the form group directive is available
    if (this.#controlContainer && this.controlName()) {
        // Get the control from the form group directive
        const control = this.#controlContainer.control?.get(this.controlName());

        if (control) {
            // Subscribe to the control's errors and the form group directive's ngSubmit event
            this.subscribeToControlErrors(control);
        } else {
            console.error(`Control "${this.controlName}" not found in the form group.`);
        }
    } else {
        console.error('FormControlErrorComponent must be used within a FormGroupDirective and "controlName" must be provided.');
    }
  })

  private subscribeToControlErrors(control: AbstractControl) {
    this.#subscription.unsubscribe();
    const formSubmit$ = 'ngSubmit' in this.#controlContainer ? (this.#controlContainer as any).ngSubmit : [];

    this.#subscription = merge(control.valueChanges, formSubmit$)
      .pipe(distinctUntilChanged())
      .subscribe(() => {
        const controlErrors = control.errors;
        const errorMessage = this.getErrorMessage(controlErrors);
        this.message.set(errorMessage);
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
    const getError = this.#errors[firstErrorKey];

    // Get the custom error message if provided, otherwise default error message
    const errorText = this.customErrors()?.[firstErrorKey] || getError(errors[firstErrorKey]);
    return errorText;
  }

  ngOnDestroy(): void {
    // Clean up the subscription
    this.#subscription.unsubscribe();
  }
}
