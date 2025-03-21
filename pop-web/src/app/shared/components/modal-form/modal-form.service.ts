import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ModalFormService {
  private modalSubject = new Subject<any>();
  modal$ = this.modalSubject.asObservable();

  open(component: any, data: any = {}, onSave: any = null, caseId?: string | null) {
    this.modalSubject.next({ component, data, onSave, caseId });
  }

  close() {
    this.modalSubject.next(null);
  }
}