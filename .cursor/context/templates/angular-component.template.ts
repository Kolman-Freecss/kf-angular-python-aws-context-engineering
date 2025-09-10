import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

// TODO: Importar modelos específicos
// import { YourModel } from '../models/your-model.interface';

// TODO: Importar servicios específicos
// import { YourService } from '../services/your.service';

// TODO: Importar selectores NgRx si es necesario
// import { selectYourData } from '../store/your.selectors';

@Component({
  selector: 'app-{{component-name}}',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div data-testid="{{component-name}}-container">
      <h2>{{component-title}}</h2>
      
      @if (loading()) {
        <div data-testid="loading">Cargando...</div>
      } @else {
        <div data-testid="content">
          <!-- TODO: Implementar contenido específico -->
        </div>
      }
    </div>
  `
})
export class {{ComponentName}}Component implements OnInit {
  // TODO: Inyectar servicios necesarios
  // private yourService = inject(YourService);
  // private store = inject(Store);
  // private fb = inject(FormBuilder);
  
  // Signals para estado local
  loading = signal(false);
  data = signal<any[]>([]);
  
  // Formularios reactivos
  // form: FormGroup = this.fb.group({
  //   field: ['', Validators.required]
  // });
  
  // Selectores NgRx
  // data$ = this.store.select(selectYourData);
  
  ngOnInit() {
    this.loadData();
  }
  
  private loadData() {
    this.loading.set(true);
    // TODO: Implementar carga de datos
    // this.yourService.getData().subscribe({
    //   next: (data) => {
    //     this.data.set(data);
    //     this.loading.set(false);
    //   },
    //   error: (error) => {
    //     console.error('Error loading data:', error);
    //     this.loading.set(false);
    //   }
    // });
  }
  
  // TODO: Implementar métodos específicos del componente
}
