import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ConceptSelectorComponent } from './concept-selector.component';
import { of } from 'rxjs';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { MessageService } from 'primeng/api';
import { Button } from 'primeng/button';
import { RadioButton } from 'primeng/radiobutton';
import { CommonModule } from '@angular/common';
import { By } from '@angular/platform-browser';

import { TerminologyService } from '../../openapi/api/terminology.service';
import { PaginatedCodedConceptSchema } from '../../openapi';

// Mock the TerminologyService
class MockTerminologyService {
  getTerminologyConcepts() {
    return of({
      count: 10,
      items: [
        { display: 'Concept A', code: 'A001', synonyms: [], system: ''},
        { display: 'Concept B', code: 'B002', synonyms: [], system: '' },
        { display: 'Concept C', code: 'C003', synonyms: [], system: '' },
      ]
      } as PaginatedCodedConceptSchema);
  }
}

describe('ConceptSelectorComponent', () => {
    let component: ConceptSelectorComponent;
    let fixture: ComponentFixture<ConceptSelectorComponent>;
    let mockTerminologyService: MockTerminologyService;

    beforeEach(async () => {
        mockTerminologyService = new MockTerminologyService();
    
        await TestBed.configureTestingModule({
          imports: [CommonModule, FormsModule, ReactiveFormsModule, AutoCompleteModule, Button, RadioButton],
          providers: [
            MessageService,
            { provide: TerminologyService, useValue: mockTerminologyService },
          ],
        }).compileComponents();
      });
    
      beforeEach(() => {
        fixture = TestBed.createComponent(ConceptSelectorComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
      });

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    describe('ngOnInit', () => {
        it('should call getTerminologyConcepts and set concepts correctly', () => {
        spyOn(mockTerminologyService, 'getTerminologyConcepts').and.callThrough();

        component.terminology = 'testTerminology';
        component.ngOnInit();
        fixture.detectChanges();

        expect(mockTerminologyService.getTerminologyConcepts).toHaveBeenCalled();
        expect(component.concepts.length).toBe(3);
        expect(component.terminologySize).toBe(10);
        expect(component.subsetSize).toBe(3);
        expect(component.concepts[0].code).toBe('A001');
        });
    });

    describe('updateConcepts', () => {
        it('should update concepts when autocomplete query changes', () => {
        spyOn(mockTerminologyService, 'getTerminologyConcepts').and.callThrough();

        component.updateConcepts({ originalEvent: new Event('input'), query: 'A' });
        fixture.detectChanges();

        expect(mockTerminologyService.getTerminologyConcepts).toHaveBeenCalled();
        expect(component.concepts.length).toBe(3);
        expect(component.concepts[0].code).toBe('A001');
        });
    });

    describe('writeValue', () => {
        it('should update the formControl value', () => {
        const value = { code: 'A001', display: 'Concept A' };
        component.writeValue(value);
        fixture.detectChanges();

        expect(component.formControl.value).toEqual(value);
        });
    });
    
    describe('Template Rendering', () => {      
      
        it('should render footer message when more concepts exist than the limit', () => {
          component.terminology = 'testTerminology';
          component.conceptsLimit = 100;
          component.terminologySize = 200;
          component.subsetSize = 100;
          component.widget = 'autocomplete';
          component.ngOnInit();
          fixture.detectChanges();  // Trigger initial change detection
      
          // Simulate typing a query in the autocomplete to trigger the footer visibility
          const input = fixture.debugElement.query(By.css('input.p-inputtext'));
          input.nativeElement.value = 'test';
          input.nativeElement.dispatchEvent(new Event('input')); // Trigger input event
          fixture.detectChanges(); // Trigger change detection to update the UI
      
          // Wait for the footer message to appear
          fixture.whenStable().then(() => {
            const footerMessage = fixture.debugElement.query(By.css('.footer-message'));
            expect(footerMessage.nativeElement.textContent).toContain('Showing 100 out of 200 entries');
          });
        });
      
        it('should render radio button widget when widget is set to "radio"', () => {
          component.terminology = 'testTerminology';
          component.widget = 'radio';
          component.ngOnInit();
          fixture.detectChanges();
      
          // Check that the radio button is rendered
          const radioButton = fixture.debugElement.query(By.css('p-radiobutton'));
          expect(radioButton).toBeTruthy();
        });
      });
});