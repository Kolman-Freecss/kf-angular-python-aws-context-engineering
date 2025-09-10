# Patrón de Arquitectura Angular 20

## Estructura de Carpetas

```
src/app/
├── features/           # Módulos de funcionalidad
│   ├── users/
│   │   ├── components/
│   │   ├── services/
│   │   ├── store/      # NgRx
│   │   └── models/
│   └── products/
├── shared/            # Componentes compartidos
│   ├── components/
│   ├── services/
│   └── models/
└── core/              # Servicios core
    ├── services/
    └── guards/
```

## Patrones de Componentes

### Standalone Components
```typescript
@Component({
  selector: 'app-feature',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `...`
})
```

### Signals para Estado Local
```typescript
export class MyComponent {
  data = signal<Data[]>([]);
  loading = signal(false);
  
  updateData(newData: Data[]) {
    this.data.set(newData);
  }
}
```

### NgRx para Estado Global
```typescript
// Actions
export const loadUsers = createAction('[Users] Load Users');
export const loadUsersSuccess = createAction(
  '[Users] Load Users Success',
  props<{ users: User[] }>()
);

// Reducer
export const usersReducer = createReducer(
  initialState,
  on(loadUsers, (state) => ({ ...state, loading: true })),
  on(loadUsersSuccess, (state, { users }) => ({ 
    ...state, 
    users, 
    loading: false 
  }))
);
```

## Inyección de Dependencias

```typescript
// Usar @inject en lugar de constructor injection
export class MyService {
  private http = inject(HttpClient);
  private store = inject(Store);
}
```
