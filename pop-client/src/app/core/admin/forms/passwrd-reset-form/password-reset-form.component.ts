import { Component, inject, Input, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AbstractFormBase } from 'src/app/features/forms/abstract-form-base.component';
import { AccessRoles, AuthService, User, UserCreate, UserPasswordReset } from 'src/app/shared/openapi';
import { Key as KeyIcon } from 'lucide-angular';
import { Button } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { FormControlErrorComponent } from 'src/app/shared/components';
import { RadioButtonModule } from 'primeng/radiobutton';
import { Fluid } from 'primeng/fluid';


@Component({
  standalone: true,
  selector: 'pop-password-reset-dialog',
  template: `  
    <p-fluid>
        <form  [formGroup]="form" (ngSubmit)="onSave()">
            
            <div class="field" *ngIf="!initialData.isAdmin">
                <label class="form-label required">Old Password</label>
                <input type="password" pInputText formControlName="oldPassword" />
                <pop-form-control-error controlName="oldPassword"/>
            </div>
            <div class="field">
                <label class="form-label required">New Password</label>
                <input type="password" pInputText formControlName="newPassword" />
                <pop-form-control-error controlName="newPassword"/>
            </div>
            <div class="field">
                <label class="form-label required">Confirm the new password</label>
                <input type="password" pInputText formControlName="newPasswordCheck" />
                <pop-form-control-error controlName="newPasswordCheck"/>
            </div>

            <p-button 
                type="submit" 
                label="Submit" 
                styleClass="w-full p-3 mt-2"  
                [loading]="loading"
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
  ],
})
export class PasswordResetFormComponent extends AbstractFormBase implements OnInit {

    private readonly authService: AuthService = inject(AuthService);
    public readonly formBuilder = inject(FormBuilder);
    
    public createService: any;
    public updateService: any;

    public readonly title: string = 'Reset password';
    public readonly subtitle: string = '';
    public readonly icon = KeyIcon;
    public initialData!: {isAdmin: boolean, user: User};

    ngOnInit() {
        // Construct the form 
        this.constructForm()
        // Dynamically set the corresponding service
        if (this.initialData.isAdmin) {
            this.createService = (payload: any) => this.authService.resetUserPassword({userId: this.initialData.user.id, password: payload});
        } else {
            this.createService = (payload: any) => this.authService.updateUserPassword({userId: this.initialData.user.id, userPasswordReset: payload});
        }
        this.updateService = () => {null}; 
    }

    constructForm(): void {
        if (this.initialData.isAdmin) {
            this.form = this.formBuilder.group({
                newPassword: [null,Validators.required],
                newPasswordCheck: [null,Validators.required],
            });
        } else {
            this.form = this.formBuilder.group({
                oldPassword: [null,Validators.required],
                newPassword: [null,Validators.required],
                newPasswordCheck: [null,Validators.required],
            });

        }
    }


    constructAPIPayload(data: any): UserPasswordReset | string {    
        if (this.initialData.isAdmin) {
            return data.newPassword
        } else {
            return {
                oldPassword: data.oldPassword,
                newPassword: data.newPassword,
            };
        }
    }

}