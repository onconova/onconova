// dynamic-form-modal.component.ts
import { Component, ViewChild, ViewContainerRef, inject, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';

import { AvatarModule } from 'primeng/avatar';
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';

import { ModalFormService } from './modal-form.service'

import { PatientFormComponent } from 'src/app/case-browser/components/patient-form/patient-form.component';


@Component({
  selector: 'app-dynamic-modal-form',
  templateUrl: './modal-form.component.html',
  styleUrl: './modal-form.component.css',
  standalone: true,
  imports: [
    CommonModule,
    AvatarModule,
    DialogModule,
    ButtonModule,
  ],
})
export class ModalFormComponent {
  @ViewChild("formContent", { read: ViewContainerRef, static: true}) content!: ViewContainerRef;
  @Output() saveEvent = new EventEmitter<any>();

  loading: boolean = false
  visible: boolean = false
  form!: FormGroup;
  formComponent: any = PatientFormComponent;
  private currentInstance: any;

  private modalService = inject(ModalFormService)

  ngAfterViewInit() {
      this.modalService.modal$.subscribe((modalData) => {
        if (modalData) {
          this.loadComponent(modalData.component, modalData.data);
        } else {
          this.closeModal();
        }
      });
  }


  private loadComponent(component: any, data: any) {
    this.content.clear();
    const componentRef = this.content.createComponent(component);
    this.currentInstance = componentRef.instance;

    // subscribe to the save event emitted by the PatientFormComponent
    this.currentInstance.save.subscribe((event: any) => {
      console.log('PROPAGATE SAVE')
      this.saveEvent.emit(event);
    });

    // Pass data to the component
    if (data) {
      Object.assign(this.currentInstance, data);
    }

    // Optionally subscribe to save/close events
    if (this.currentInstance.save) {
      this.currentInstance.save.subscribe(() => {
        this.visible = false; // Close modal on save
      });
    }

    this.visible = true;
  }

  private closeModal() {
    this.visible = false;
    if (this.currentInstance?.close) {
      this.currentInstance.close();
    }
  }


  onClose() {
    console.log('CLOSE')
    this.closeModal();
  }
}