import { Component, Output, EventEmitter, inject, DestroyRef } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { concatMap, forkJoin, map, of, tap } from 'rxjs';

import { MessageService } from 'primeng/api';

import { Ribbon } from 'lucide-angular';
import { EmptyObject } from 'chart.js/dist/types/basic';
import { Call } from '@angular/compiler';
import { PatientCase } from 'src/app/shared/openapi';

interface Resource {
    id: string;
    [key: string]: any;
  }
@Component({
    template: ''
})
export abstract class AbstractFormBase {

  private readonly messageService = inject(MessageService)
  public readonly destroyRef = inject(DestroyRef);

  @Output() public save = new EventEmitter<void>();

  public form!: FormGroup;
  abstract initialData: Resource | EmptyObject;  
  public loading: boolean = false;


  abstract readonly title: string;
  abstract readonly subtitle: string;
  abstract readonly icon: any;


  abstract createService: CallableFunction;
  abstract updateService: CallableFunction;
  public subformsServices: {
    condition?: CallableFunction | null,
    payloads: CallableFunction, 
    deletedEntries: CallableFunction, 
    delete: CallableFunction, 
    create: CallableFunction, 
    update: CallableFunction
  }[] = [];
  
  abstract constructAPIPayload(data: any): any

  onSave(): void {
    if (this.form.valid) {
      this.loading = true;  
      // Prepare the data according to the API scheme
      const data = this.form.value
      const payload = this.constructAPIPayload(data)
      // Send the data to the server's API
      const updating = this.initialData && this.initialData.id;
      if (updating) {

        let subformsUpdates$ = this.subformsServices.flatMap((subformServices) => {
          if (!subformServices?.condition || (subformServices?.condition && subformServices.condition(data))) {
            return subformServices.payloads(data).map(
              (subformPayload: any) => {
                if (subformPayload.id) {
                  return subformServices.update(this.initialData.id, subformPayload.id, subformPayload)
                } else {
                  return subformServices.create(this.initialData.id, subformPayload)
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
            (deletedEntryId: any) => subformServices.delete(this.initialData.id, deletedEntryId)
          )
        } else {
          return []
        }
      })

      forkJoin([
          this.updateService(this.initialData.id, payload),
          ...subformsUpdates$,
          ...subformDeletions$,
      ]).pipe(
        takeUntilDestroyed(this.destroyRef)
      ).subscribe({
            next: () => {
              // Report the successful creation of the resource
              this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Updated ' + this.initialData.id });
              this.loading = false;  
              this.save.emit();
            },
            error: (error: Error) => {
              // Report any problems
              this.loading = false;  
              this.messageService.add({ severity: 'error', summary: 'Error ocurred while updating', detail: error.message });
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
          takeUntilDestroyed(this.destroyRef)
        )
        .subscribe({
          next: (response: Resource) => {
            // Report the successful creation of the resource
            this.messageService.add({ severity: 'success', summary: 'Success', detail: 'Saved '+ this.title.toLowerCase() + response.id });
            this.loading = false;  
            this.save.emit();
          },
          error: (error: Error) => {
            // Report any problems
            this.loading = false;  
            this.messageService.add({ severity: 'error', summary: 'Error ocurred while saving', detail: error.message });
            console.error(error)
          }
        })  
      }
    }
  }
}