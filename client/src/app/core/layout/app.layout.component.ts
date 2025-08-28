import { Component, DestroyRef, Renderer2, ViewChild, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterModule } from '@angular/router';
import { LayoutService } from './app.layout.service';
import { Toast } from 'primeng/toast';
import { AppTopBarComponent } from './components/app.topbar.component';
import { AppFooterComponent } from './components/app.footer.component';
import { AppSidebarMenuComponent } from './components/app.sidebar-menu.component';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'onconova-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    AppTopBarComponent,
    AppFooterComponent,
    AppSidebarMenuComponent,
  ],
  templateUrl: './app.layout.component.html'
})
export class AppLayoutComponent {
  @ViewChild(AppSidebarMenuComponent) appSidebar!: AppSidebarMenuComponent;
  @ViewChild(AppTopBarComponent) appTopbar!: AppTopBarComponent;

  private menuOutsideClickListener: (() => void) | null = null;
  private profileMenuOutsideClickListener: (() => void) | null = null;

  constructor(
    public layoutService: LayoutService,
    public renderer: Renderer2,
    public router: Router,
    private destroyRef: DestroyRef
  ) {
    // React to overlay open signal
    effect(() => {
      this.layoutService.overlayOpenSignal();
      this.setupOutsideClickListeners();

      if (this.layoutService.isStaticMenuMobileActive()) {
        this.blockBodyScroll();
      }
    });

    // On route changes: clean up menus
    this.router.events
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(event => {
        if (event instanceof NavigationEnd) {
          this.hideMenu();
          this.hideProfileMenu();
        }
      });
  }

  private setupOutsideClickListeners() {
    // Menu click listener
    if (!this.menuOutsideClickListener) {
      this.menuOutsideClickListener = this.renderer.listen('document', 'click', event => {
        const target = event.target as HTMLElement;
        const clickedOutside = !(
          this.appSidebar?.el.nativeElement.contains(target) ||
          this.appTopbar?.menuButtonRef()?.nativeElement.contains(target)
        );

        if (clickedOutside) {
          this.hideMenu();
        }
      });
    }

    // Profile menu click listener
    if (!this.profileMenuOutsideClickListener) {
      this.profileMenuOutsideClickListener = this.renderer.listen('document', 'click', event => {
        const target = event.target as HTMLElement;
        const clickedOutside = !(
          this.appTopbar?.menuRef()?.nativeElement.contains(target) ||
          this.appTopbar?.topbarMenuButtonRef()?.nativeElement.contains(target)
        );

        if (clickedOutside) {
          this.hideProfileMenu();
        }
      });
    }
  }

  hideMenu() {
    this.layoutService.isOverlayMenuActive.set(false);
    this.layoutService.isStaticMenuMobileActive.set(false);
    this.layoutService.isMenuHoverActive.set(false);

    if (this.menuOutsideClickListener) {
      this.menuOutsideClickListener();
      this.menuOutsideClickListener = null;
    }

    this.unblockBodyScroll();
  }

  hideProfileMenu() {
    this.layoutService.isProfileSidebarVisible.set(false);

    if (this.profileMenuOutsideClickListener) {
      this.profileMenuOutsideClickListener();
      this.profileMenuOutsideClickListener = null;
    }
  }

  blockBodyScroll(): void {
    document.body.classList.add('blocked-scroll');
  }

  unblockBodyScroll(): void {
    document.body.classList.remove('blocked-scroll');
  }

  get containerClass() {
    return {
      'layout-overlay': this.layoutService.config.menuMode === 'overlay',
      'layout-static': this.layoutService.config.menuMode === 'static',
      'layout-static-inactive': this.layoutService.isStaticMenuDesktopInactive() && this.layoutService.config.menuMode === 'static',
      'layout-overlay-active': this.layoutService.isOverlayMenuActive(),
      'layout-mobile-active': this.layoutService.isStaticMenuMobileActive(),
      'p-input-filled': this.layoutService.config.inputStyle === 'filled',
      'p-ripple-disabled': !this.layoutService.config.ripple
    };
  }
}
