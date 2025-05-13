import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterModule  } from '@angular/router';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { filter } from 'rxjs/operators';
import { MenuItem } from 'primeng/api';

@Component({
    selector: '[pop-menuitem]',
    imports: [
        CommonModule,
        RouterModule,
    ],
    template: `
		<ng-container>
            @if ( item().visible !== false ) {
                @if (root()) {
                    <div class="layout-menuitem-root-text">
                        {{item().label}}
                    </div>
                } 
                @else if (!item().routerLink || item().items) {
                    <a [attr.href]="item().url" (click)="itemClick($event)"
                    [attr.target]="item().target" tabindex="0" pRipple>
                        <i [ngClass]="item().icon" class="layout-menuitem-icon"></i>
                        <span class="layout-menuitem-text">{{item().label}}</span>
                    </a>
                }
                @else if ((item().routerLink) && !item().items) {
                    <a (click)="itemClick($event)" [ngClass]="item()['class']" 
                        [routerLink]="item().routerLink" routerLinkActive="active-route" [routerLinkActiveOptions]="item().routerLinkActiveOptions||{ paths: 'exact', queryParams: 'ignored', matrixParams: 'ignored', fragment: 'ignored' }"
                        [fragment]="item().fragment" [queryParamsHandling]="item().queryParamsHandling" [preserveFragment]="item().preserveFragment" 
                        [skipLocationChange]="item().skipLocationChange" [replaceUrl]="item().replaceUrl" [state]="item().state" [queryParams]="item().queryParams"
                        [attr.target]="item().target" tabindex="0" pRipple>
                        <i [ngClass]="item().icon" class="layout-menuitem-icon"></i>
                        <span class="layout-menuitem-text">{{item().label}}</span>
                    </a>
                }
                @if (item().items) {
                    <ul [@children]="submenuAnimation()">
                        <ng-template ngFor let-child let-i="index" [ngForOf]="item().items">
                            <li pop-menuitem [item]="child" [index]="i" [parentKey]="key()" [class]="child['badgeClass']"></li>
                        </ng-template>
                    </ul>
                }
            }
		</ng-container>
    `,
    animations: [
        trigger('children', [
            state('collapsed', style({
                height: '0'
            })),
            state('expanded', style({
                height: '*'
            })),
            transition('collapsed <=> expanded', animate('400ms cubic-bezier(0.86, 0, 0.07, 1)'))
        ])
    ],
    host: { 
        'class.layout-root-menuitem': 'root()',
        'class.active-menuitem': 'active() && !root()'
    },
})
export class AppMenuitemComponent {

    // Component input signal properties
    public item = input.required<MenuItem>();
    public index = input.required<number>();
    public root = input<boolean>(false);
    public parentKey = input<string>();

    // Injected services 
    readonly #router = inject(Router);

    // Reactive properties
    public active = signal<boolean>(false);
    public routerSignal = signal<NavigationEnd | null>(null);

    // Computed properties
    public key = computed<string>(() => this.parentKey ? this.parentKey + '-' + this.index : String(this.index))
    public submenuAnimation = computed(() => this.root() ? 'expanded' : (this.active() ? 'expanded' : 'collapsed'));


    #activeRouteEffect = effect(() => {
        if (this.item().routerLink && this.routerSignal()) {
            const isActive = this.#router.isActive(this.item().routerLink[0], { paths: 'exact', queryParams: 'ignored', matrixParams: 'ignored', fragment: 'ignored' });
            this.active.set(isActive);
        }
    });

    ngOnInit() {
        // reactive effect: watch route changes and update active state
        this.#router.events.pipe(filter(e => e instanceof NavigationEnd)).subscribe(event => {
            this.routerSignal.set(event as NavigationEnd);
        });
    }

    itemClick(event: Event) {
        if (this.item().disabled) {
          event.preventDefault();
          return;
        }
    
        if (this.item().command) {
          this.item().command!({ originalEvent: event, item: this.item });
        }
    
        if (this.item().items) {
          this.active.update(value => !value);
        }
      }
}
