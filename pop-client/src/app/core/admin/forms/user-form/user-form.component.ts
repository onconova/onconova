import { Component, computed, effect, inject, input } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AbstractFormBase } from 'src/app/features/forms/abstract-form-base.component';
import { AccessRoles, UsersService, User, UserCreate } from 'src/app/shared/openapi';
import { Fluid } from 'primeng/fluid';
import { Button } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { FormControlErrorComponent } from 'src/app/shared/components';
import { RadioButtonModule } from 'primeng/radiobutton';


@Component({
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
    ]
})
export class UserFormComponent extends AbstractFormBase {

    // Input signal for initial data passed to the form
    initialData = input<User>();

    // Service injections
    readonly #usersService = inject(UsersService);
    readonly #fb = inject(FormBuilder);
    
    // Create and update service methods for the form data
    public readonly createService = (payload: UserCreate) => this.#usersService.createUser({userCreate: payload});
    public readonly updateService = (id: string, payload: UserCreate) => this.#usersService.updateUser({userId: id, userCreate: payload});

    // Define the form
    public form = this.#fb.group({
        username: this.#fb.control<string | null>(null, Validators.required),
        firstName: this.#fb.control<string | null>(null, Validators.required),
        lastName: this.#fb.control<string | null>(null, Validators.required),
        email: this.#fb.control<string | null>(null, Validators.required),
        organization: this.#fb.control<string | null>(null),
        department: this.#fb.control<string | null>(null),
        accessLevel: this.#fb.control<number | null>(1, Validators.required),
    });

    readonly #onInitialDataChangeEffect = effect((): void => {
        const data = this.initialData();
        if (!data) return;
        
        this.form.patchValue({
            username: data.username ?? null,
            firstName: data.firstName ?? null,
            lastName: data.lastName ?? null,
            email: data.email ?? null,
            organization: data.organization ?? null,
            department: data.department ?? null,
            accessLevel: data.accessLevel || 1,
        });

        // Username if non-editable
        this.form.get('username')?.disable(); 

        if (data.isProvided) {
            Object.keys(this.form.controls).forEach((controlName) => {
                if (controlName !== 'accessLevel') {
                    this.form.get(controlName)?.disable();
                }
            });
        }


    });
    provider = computed(() => this.initialData()?.provider);

    // API Payload construction function
    readonly payload = (): UserCreate => { 
        this.form.get('username')?.enable(); 
        const data = this.form.value;   
        return {
            username: data.username!,
            firstName: data.firstName,
            lastName: data.lastName,
            email: data.email,
            organization: data.organization,
            department: data.department,
            accessLevel: data.accessLevel!,
        };
    }

    // Human readable choices for UI elements
    public roles = [
        {label: AccessRoles.External, accessLevel: 0},
        {label: AccessRoles.Viewer, accessLevel: 1},
        {label: AccessRoles.DataContributor, accessLevel: 2},
        {label: AccessRoles.DataAnalyst, accessLevel: 3},
        {label: AccessRoles.ProjectManager, accessLevel: 4},
        {label: AccessRoles.PlatformManager, accessLevel: 5},
        {label: AccessRoles.SystemAdministrator, accessLevel: 6},
    ]


}