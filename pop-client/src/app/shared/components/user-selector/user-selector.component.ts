import { Component, forwardRef, inject, input, output, signal } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { map } from 'rxjs';

import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';

import { User, UsersService } from 'pop-api-client';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
    selector: 'pop-user-selector',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => UserSelectorComponent),
            multi: true,
        },
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        AutoCompleteModule,
    ],
    template: `
    <p-autoComplete
        [formControl]="formControl"
        (onSelect)="onChange.emit($event.value)"
        [dropdown]="true"
        [showClear]="true"
        [attr.disabled]="disabled()"
        [forceSelection]="true"
        optionLabel="fullName"
        [suggestions]="userSuggestions.value() || []"
        (completeMethod)="query.set($event.query); userSuggestions.reload()"
        [multiple]="multiple()"
        [unique]="true"
        [completeOnFocus]="true"
        [placeholder]="placeholder()"
        appendTo="body"/>
    `
})
export class UserSelectorComponent implements ControlValueAccessor {

    readonly multiple = input<boolean>(false);
    readonly disabled = input<boolean>(false);
    readonly placeholder = input<string>('Select or search an option');
    readonly returnUsername = input<boolean>(true);
    readonly onChange = output<User>();

    readonly #usersService = inject(UsersService);

    public formControl: FormControl = new FormControl();
    
    public query = signal<string>('');
    public userSuggestions = rxResource({
        request: () => ({fullNameContains: this.query(), limit: 20}),
        loader: ({request}) => this.#usersService.getUsers(request).pipe(map(response => response.items))
    })

    writeValue(value: any): void {
        if (this.returnUsername()) {
            if (value) {
                // Find the concept by code
                this.#usersService.getUsers({usernameAnyOf: this.multiple() ? value : undefined, username: this.multiple() ? undefined : value}).subscribe({
                    next: (response) => {
                        if (this.multiple()) {
                            this.formControl.patchValue(
                                value.map((username: string) => response.items.find((user:User) => user.username === username))
                            );
                        } else {
                            this.formControl.patchValue(response.items.find((user:User) => user.username === value));
                        }
                    },
                })
            } else {
                this.formControl.patchValue(value);
            }
        } else {
            this.formControl.patchValue(value);
        }
    }

    registerOnChange(fn: any): void {
        this.formControl.valueChanges.subscribe((val) => {
            if (this.returnUsername()) {
                if (this.multiple()) {
                    fn(val ? val.map((c: User) => c.username) : []);
                } else {
                    fn(val ? val.username : null);
                }
            } else {
                fn(val);
            }
        });
    }

    registerOnTouched(fn: any): void {
        this.formControl.valueChanges.subscribe(val => fn(val));
    }
}