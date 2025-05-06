import { Component, Output, EventEmitter, inject, DestroyRef, input, InputSignal, WritableSignal, signal } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin, map, Observable, of } from 'rxjs';
import { MessageService } from 'primeng/api';

import { EmptyObject } from 'chart.js/dist/types/basic';
import { ModifiedResource } from 'src/app/shared/openapi';
import { DynamicDialogRef } from 'primeng/dynamicdialog';

interface Resource {
    id: string;
    [key: string]: any;
  }
interface ResourceCreate {
    [key: string]: any;
  }
@Component({
    template: ''
})
export abstract class AbstractFormBase {

  #dynamicDialogRef  = inject(DynamicDialogRef)
  #messageService = inject(MessageService)

  form!: FormGroup;
  
  caseId: InputSignal<string> = input.required<string>();
  resourceId: InputSignal<string | undefined> = input<string>();
  isSaving: WritableSignal<boolean> = signal(false);
  subformsServices: {
    condition?: (data: any) => boolean | null,
    payloads: (data: any) => any[],
    deletedEntries:  () => string[], 
    delete: (parentId: string, id: string) => Observable<any>, 
    create: (parentId: string, payload: any) => Observable<ModifiedResource>, 
    update: (parentId: string, id: string, payload: any) => Observable<ModifiedResource>, 
  }[] = [];

  abstract initialData: InputSignal<any>;
  abstract createService (payload: ResourceCreate): any;
  abstract updateService (id: string, payload: ResourceCreate): any;
  abstract constructAPIPayload(data: any): any

  onSave(): void {
    if (this.form.valid) {
      this.isSaving.set(true);  
      // Prepare the data according to the API scheme
      const data = this.form.value
      const payload = this.constructAPIPayload(data)
      // Send the data to the server's API
      if (this.resourceId()) {
        const resourceId = this.resourceId() as string;
        let subformsUpdates$ = this.subformsServices.flatMap((subformServices) => {
          if (!subformServices?.condition || (subformServices?.condition && subformServices.condition(data))) {
            return subformServices.payloads(data).map(
              (subformPayload: any) => {
                if (subformPayload.id) {
                  return subformServices.update(resourceId, subformPayload.id, subformPayload)
                } else {
                  return subformServices.create(resourceId, subformPayload)
                }
              }
            )
          } else {
            return []
          }
        }
      );

      let subformDeletions$ = this.subformsServices.flatMap((subformServices, index) => {
        if (!subformServices?.condition || (subformServices?.condition && subformServices.condition(data))) {
          const toBeDeleted = subformServices.deletedEntries()
          if (toBeDeleted.length == 0 ) {
            return []
          }
          return toBeDeleted.map(
            (deletedEntryId: any) => subformServices.delete(resourceId, deletedEntryId)
          )
        } else {
          return []
        }
      })
      forkJoin([
          this.updateService(resourceId, payload),
          ...subformsUpdates$,
          ...subformDeletions$,
      ]).subscribe({
          next: (response: ModifiedResource[]) => {
              // Report the successful creation of the resource
              this.#messageService.add({ severity: 'success', summary: 'Success', detail: 'Updated ' + response[0].description });
              this.isSaving.set(false); 
              this.#dynamicDialogRef?.close({saved: true});
            },
            error: (error: any) => {
              // Report any problems
              this.isSaving.set(false); 
              this.#messageService.add({ severity: 'error', summary: 'Error ocurred while updating', detail: error.error ? error.error.detail : error.message });
              this.#dynamicDialogRef?.close({saved: false});
              console.error(error)
            }
          })
  
      } else {

        this.createService(payload)        
        .pipe(
          map((response: Resource) => {
            // Handle the case where there are no secondService defined
            if (!this.subformsServices || this.subformsServices.length === 0) {
              return of(response);
            }
            // Use the returned resource ID as input for the second requests
            return forkJoin(
              ...this.subformsServices.flatMap((subformServices) => {
                if (!subformServices?.condition || (subformServices?.condition && subformServices.condition(data))) {
                  return subformServices.payloads(data).map(
                    (subformPayload: any) => subformServices.create(response.id, subformPayload)
                  )
                } else {
                  return [];
                }
              })
            )
          }),
        )
        .subscribe({
          next: (response: ModifiedResource) => {
            // Report the successful creation of the resource
            this.#messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved ' + response.description });
            this.isSaving.set(false); 
            this.#dynamicDialogRef?.close({saved: true});
          },
          error: (error: any) => {
            // Report any problems
            this.isSaving.set(false); 
            this.#messageService.add({ severity: 'error', summary: 'Error ocurred while saving', detail: error.error ? error.error.detail : error.message });
            this.#dynamicDialogRef?.close({saved: false});
            console.error(error)
          }
        })  
      }
    }
  }
}