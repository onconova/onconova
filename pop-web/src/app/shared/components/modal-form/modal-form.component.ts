// dynamic-form-modal.component.ts
import { Component, ViewChild, ViewContainerRef, inject, Output, Input, EventEmitter, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';

import { AvatarModule } from 'primeng/avatar';
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';

import { LucideAngularModule } from 'lucide-angular';

import { ModalFormService } from './modal-form.service'

@Component({
  standalone: true,
  selector: 'pop-dynamic-modal-form',
  templateUrl: './modal-form.component.html',
  styleUrl: './modal-form.component.css',
  encapsulation: ViewEncapsulation.None,
  imports: [
    LucideAngularModule,
    CommonModule,
    AvatarModule,
    DialogModule,
    ButtonModule,
    DividerModule,
  ],
})
export class ModalFormComponent {
  @ViewChild("formContent", { read: ViewContainerRef, static: true}) content!: ViewContainerRef;
  @Output() saveEvent = new EventEmitter<any>();

  caseId: string | null = null
  loading: boolean = false
  visible: boolean = false
  title!: string;
  subtitle!: string;
  formComponent: any;
  private modalService = inject(ModalFormService)

  ngAfterViewInit() {
      this.modalService.modal$.subscribe((modalData) => {
        if (modalData) {
          this.loadComponent(modalData.component, modalData.data, modalData.onSave, modalData.caseId);
        } else {
          this.closeModal();
        }
      });
  }


  private loadComponent(component: any, data: any, onSave: any, caseId?: string | null) {
    this.content.clear();
    const componentRef = this.content.createComponent(component);
    this.formComponent = componentRef.instance;
    this.formComponent.caseId = caseId;

    // subscribe to the save event emitted by the PatientFormComponent
    this.formComponent.save.subscribe((event: any) => {
      if (onSave) {
        onSave()
      }
      this.saveEvent.emit(event);
    });

    // Pass data to the component
    if (data) {
      this.formComponent.initialData = data;
    }

    // Optionally subscribe to save/close events
    if (this.formComponent.save) {
      this.formComponent.save.subscribe(() => {
        this.visible = false; // Close modal on save
      });
    }

    this.visible = true;
  }

  private closeModal() {
    this.visible = false;
    if (this.formComponent?.close) {
      this.formComponent.close();
    }
  }


  onClose() {
    this.closeModal();
  }
}