/**
 * UserSelectorComponent is an Angular form control for selecting users from a remote API.
 * It provides an autocomplete dropdown powered by PrimeNG's AutoComplete component,
 * supporting both single and multiple selection modes. The component can return either
 * the selected User object(s) or just their username(s), depending on the `returnUsername` input.
 *
 * - Autocomplete user search by full name or username.
 * - Configurable minimum access level for user suggestions.
 * - Supports single and multiple selection.
 * - Emits selected user(s) via `onChange` output.
 * - Integrates with Angular forms as a ControlValueAccessor.
 * - Optionally returns only usernames for form value.
 * - If a user's `fullName` is empty, their username is displayed instead.
 *
 * ```html
 * <!-- Single Selection -->
 * <onconova-user-selector
 *   [placeholder]="'Select a user'"
 *   [minAccessLevel]="2"
 *   [returnUsername]="true"
 *   [(ngModel)]="selectedUsername">
 * </onconova-user-selector>
 * ```
 *
 * ```html
 * <!-- Multiple Selection -->
 * <onconova-user-selector
 *   [multiple]="true"
 *   [returnUsername]="false"
 *   [(ngModel)]="selectedUsers">
 * </onconova-user-selector>
 * ```
 *
 */
import { Component, forwardRef, inject, input, output, signal } from '@angular/core';
import { ControlValueAccessor, FormControl, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { map } from 'rxjs';
import { CommonModule } from '@angular/common';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ReactiveFormsModule } from '@angular/forms';
import { User, UsersService } from 'onconova-api-client';
import { rxResource } from '@angular/core/rxjs-interop';


@Component({
    selector: 'onconova-user-selector',
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
    readonly minAccessLevel = input<number>(0);
    readonly placeholder = input<string>('Select or search an option');
    readonly returnUsername = input<boolean>(true);
    readonly onChange = output<User>();

    readonly #usersService = inject(UsersService);

    public formControl: FormControl = new FormControl();
    
    public query = signal<string>('');
    public userSuggestions = rxResource({
        request: () => ({fullNameContains: this.query(), limit: 20, accessLevelGreaterThanOrEqual: this.minAccessLevel()}),
        loader: ({request}) => this.#usersService.getUsers(request).pipe(map(response => response.items.map((user) => {
            if (!user.fullName.trim()) {
                user.fullName = user.username
            } else {
                user.fullName = `${user.username} (${user.fullName})`
            }
            return user
        })))
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