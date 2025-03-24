// cancer-icon.component.spec.ts
import { TestBed } from '@angular/core/testing';
import { CancerIconComponent } from './cancer-icon.component';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { HttpClient, HttpClientModule } from '@angular/common/http';

describe('CancerIconComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InlineSVGModule, HttpClientModule],
      providers: [HttpClient]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(CancerIconComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  it('should display the default icon', () => {
    const fixture = TestBed.createComponent(CancerIconComponent);
    const component = fixture.componentInstance;
    fixture.detectChanges();
    expect(component.icon).toBe(component.defaultIcon);
  });

  it('should update the icon based on the topography input', () => {
    const fixture = TestBed.createComponent(CancerIconComponent);
    const component = fixture.componentInstance;
    component.topography = 'C00';
    fixture.detectChanges();
    expect(component.icon).toBe('assets/images/body/mouth.svg');
  });

  it('should not update the icon if the topography is not found', () => {
    const fixture = TestBed.createComponent(CancerIconComponent);
    const component = fixture.componentInstance;
    component.topography = ' invalid-topography';
    fixture.detectChanges();
    expect(component.icon).toBe(component.defaultIcon);
  });
});