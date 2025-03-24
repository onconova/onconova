import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MultiReferenceSelectComponent } from './multi-reference-select.component';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MultiSelectModule } from 'primeng/multiselect';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

describe('MultiReferenceSelectComponent', () => {
  let component: MultiReferenceSelectComponent;
  let fixture: ComponentFixture<MultiReferenceSelectComponent>;
  let de: DebugElement;
  
  // Mock reference data
  const mockReferences = [
    { id: '1', description: 'Option 1' },
    { id: '2', description: 'Option 2' },
    { id: '3', description: 'Option 3' },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, CommonModule, MultiSelectModule, FormsModule],
    }).compileComponents();

    fixture = TestBed.createComponent(MultiReferenceSelectComponent);
    component = fixture.componentInstance;
    de = fixture.debugElement;

    // Setting mock input data
    component.options = mockReferences;
    fixture.detectChanges();
  });

  // Test: Verifying if the component renders
  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

});
