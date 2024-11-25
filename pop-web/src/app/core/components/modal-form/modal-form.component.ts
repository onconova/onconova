// dynamic-form-modal.component.ts
import { Component, ViewChild } from '@angular/core';

import { AvatarModule } from 'primeng/avatar';
import { DialogModule } from 'primeng/dialog';

@Component({
  selector: 'app-modal-form',
  templateUrl: './modal-form.component.html',
  styleUrl: './modal-form.component.css',
  standalone: true,
  imports: [
    AvatarModule,
    DialogModule
  ],
})
export class ModalFormComponent {
  @ViewChild('formContainer', { static: true }) formContainer: any;

  visible: boolean = false

  openModal() {
    this.visible = true;
  }

  closeModal() {
    console.log('CLOSE MODAL')
    this.visible = false;
  }
}