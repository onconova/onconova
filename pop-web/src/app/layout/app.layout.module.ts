import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { InputTextModule } from 'primeng/inputtext';
import { SidebarModule } from 'primeng/sidebar';
import { BadgeModule } from 'primeng/badge';
import { RadioButtonModule } from 'primeng/radiobutton';
import { InputSwitchModule } from 'primeng/inputswitch';
import { RippleModule } from 'primeng/ripple';
import { AppMenuComponent } from './components/menu/app.menu.component';
import { AppMenuitemComponent } from './components/menu/components/menuitem/app.menuitem.component';
import { RouterModule } from '@angular/router';
import { TieredMenuModule } from 'primeng/tieredmenu';
import { ButtonModule } from 'primeng/button';
import { MessagesModule } from 'primeng/messages';
import { ToastModule } from 'primeng/toast';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { AppTopBarComponent } from './components/topbar/app.topbar.component';
import { AppFooterComponent } from './components/footer/app.footer.component';
import { AppSidebarComponent } from "./components/sidebar/app.sidebar.component";
import { AppLayoutComponent } from "./app.layout.component";

import { MessageService } from 'primeng/api';

@NgModule({
    declarations: [
        AppMenuitemComponent,
        AppTopBarComponent,
        AppFooterComponent,
        AppMenuComponent,
        AppSidebarComponent,
        AppLayoutComponent,
    ],
    imports: [
        BrowserModule,
        FormsModule,
        HttpClientModule,
        InlineSVGModule,
        TieredMenuModule,
        ButtonModule,
        MessagesModule,
        ToastModule,
        BrowserAnimationsModule,
        InputTextModule,
        SidebarModule,
        BadgeModule,
        RadioButtonModule,
        InputSwitchModule,
        RippleModule,
        RouterModule,
    ],
    exports: [AppLayoutComponent],
    providers: [MessageService]
})
export class AppLayoutModule { }
