import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ModalFormService {
  private modalSubject = new Subject<any>();
  modal$ = this.modalSubject.asObservable();

  open(component: any, data: any = {}) {
    this.modalSubject.next({ component, data });
  }

  close() {
    this.modalSubject.next(null);
  }
}