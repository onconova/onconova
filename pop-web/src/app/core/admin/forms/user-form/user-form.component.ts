import { Component, inject, OnInit} from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AbstractFormBase } from 'src/app/features/case-forms/abstract-form-base.component';
import { AccessRoles, AuthService, UserCreate } from 'src/app/shared/openapi';
import { User } from 'lucide-angular';
import { Fluid } from 'primeng/fluid';
import { Button } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { FormControlErrorComponent } from 'src/app/shared/components';
import { RadioButtonModule } from 'primeng/radiobutton';


@Component({
  standalone: true,
  selector: 'pop-user-form',
  templateUrl: './user-form.component.html',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    Fluid,
    Button,
    PasswordModule,
    InputTextModule,
    RadioButtonModule,
    FormControlErrorComponent,
  ],
})
export class UserFormComponent extends AbstractFormBase implements OnInit {

    private readonly authService: AuthService = inject(AuthService);
    public readonly formBuilder = inject(FormBuilder);
    
    public readonly createService = (payload: UserCreate) => this.authService.createUser({userCreate: payload});
    public readonly updateService = (id: string, payload: UserCreate) => this.authService.updateUser({userId: id, userCreate: payload});

    public readonly title: string = 'User Profile';
    public readonly subtitle: string = 'Add new user';
    public readonly icon = User;
    public roles = [
        {label: AccessRoles.External, accessLevel: 0},
        {label: AccessRoles.Viewer, accessLevel: 1},
        {label: AccessRoles.DataContributor, accessLevel: 2},
        {label: AccessRoles.DataAnalyst, accessLevel: 3},
        {label: AccessRoles.ProjectManager, accessLevel: 4},
        {label: AccessRoles.PlatformManager, accessLevel: 5},
        {label: AccessRoles.SystemAdministrator, accessLevel: 6},
    ]
    public initialData: UserCreate | any = {};

    ngOnInit() {
        // Construct the form 
        this.constructForm()
    }

    constructForm(): void {
        this.form = this.formBuilder.group({
            username: [this.initialData?.username, Validators.required],
            firstName: [this.initialData?.firstName, Validators.required],
            lastName: [this.initialData?.lastName, Validators.required],
            email: [this.initialData?.email, Validators.required],
            organization: [this.initialData?.organization],
            department: [this.initialData?.department],
            accessLevel: [this.initialData?.accessLevel || 1, Validators.required],
        });
    }


    constructAPIPayload(data: any): UserCreate {    
        return {
            username: data.username,
            firstName: data.firstName,
            lastName: data.lastName,
            email: data.email,
            organization: data.organization,
            department: data.department,
            accessLevel: data.accessLevel,
        };
    }

}