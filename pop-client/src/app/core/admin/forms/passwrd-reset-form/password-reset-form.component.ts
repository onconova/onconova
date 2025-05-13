import { Component, computed, inject, input } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AbstractFormBase } from 'src/app/features/forms/abstract-form-base.component';
import { AuthService, User, UserPasswordReset } from 'src/app/shared/openapi';
import { Button } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { FormControlErrorComponent } from 'src/app/shared/components';
import { RadioButtonModule } from 'primeng/radiobutton';
import { Fluid } from 'primeng/fluid';


@Component({
    selector: 'pop-password-reset-dialog',
    template: `  
    <p-fluid>
        <form  [formGroup]="form" (ngSubmit)="submitFormData()">
            
            <input type="text" name="username" [value]="this.initialData()?.user?.username" hidden autocomplete="username" />
            @if (!initialData()?.isAdmin) {
                <div class="field">
                    <label class="form-label required">Old Password</label>
                    <input type="password" pInputText formControlName="oldPassword" autocomplete="current-password" />
                    <pop-form-control-error controlName="oldPassword"/>
                </div>
            }
            <div class="field">
                <label class="form-label required">New Password</label>
                <input type="password" pInputText formControlName="newPassword" autocomplete="new-password" />
                <pop-form-control-error controlName="newPassword"/>
            </div>
            <div class="field">
                <label class="form-label required">Confirm the new password</label>
                <input type="password" pInputText formControlName="newPasswordCheck" autocomplete="new-password" />
                <pop-form-control-error controlName="newPasswordCheck"/>
            </div>

            <p-button 
                type="submit" 
                label="Submit" 
                styleClass="w-full p-3 mt-2"  
                [loading]="isSaving()"
                [disabled]="form.invalid  || form.value.newPassword !== form.value.newPasswordCheck" />
                
        </form>
    </p-fluid>
    `,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        FormsModule,
        Button,
        Fluid,
        PasswordModule,
        InputTextModule,
        FormControlErrorComponent,
        RadioButtonModule,
    ]
})
export class PasswordResetFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<{isAdmin: boolean, user: User}>();

    // Service injections
    readonly #authService: AuthService = inject(AuthService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public createService: any;
    public updateService: any;

    // Define the form
    public form = this.#fb.group({
        oldPassword: this.#fb.control<string>('', Validators.required),
        newPassword: this.#fb.control<string>('', Validators.required),
        newPasswordCheck: this.#fb.control<string>('', Validators.required),
    });

    ngOnInit() {
        // Dynamically set the corresponding service
        if (this.initialData()?.isAdmin) {
            this.createService = (payload: any) => this.#authService.resetUserPassword({userId: this.initialData()?.user.id as string, password: payload});
        } else {
            this.createService = (payload: any) => this.#authService.updateUserPassword({userId: this.initialData()?.user.id as string, userPasswordReset: payload});
        }
        this.updateService = () => {null}; 
    }


    readonly payload = (): UserPasswordReset | string => {
        const data = this.form.value;    
        if (this.initialData()?.isAdmin) {
            return data.newPassword as string
        } else {
            return {
                oldPassword: data.oldPassword,
                newPassword: data.newPassword,
            } as UserPasswordReset;
        }
    }

}