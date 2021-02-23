import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassificationLoopComponent } from './classification-loop.component';

describe('ClassificationLoopComponent', () => {
  let component: ClassificationLoopComponent;
  let fixture: ComponentFixture<ClassificationLoopComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ClassificationLoopComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassificationLoopComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
