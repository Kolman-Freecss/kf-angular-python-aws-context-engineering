# Angular 20 Fundamentals

## Core Concepts

### Standalone Components
Angular 20 emphasizes standalone components that don't require NgModules:

```typescript
@Component({
  selector: 'app-feature',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `...`
})
export class FeatureComponent {}
```

### Signals
New reactive primitive for state management:

```typescript
export class MyComponent {
  // Writable signal
  count = signal(0);
  
  // Computed signal
  doubleCount = computed(() => this.count() * 2);
  
  // Effect for side effects
  constructor() {
    effect(() => {
      console.log('Count changed:', this.count());
    });
  }
  
  increment() {
    this.count.update(value => value + 1);
  }
}
```

### NgRx State Management
For complex state management:

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

// Selectors
export const selectUsers = (state: AppState) => state.users.users;
export const selectLoading = (state: AppState) => state.users.loading;
```

## Architecture Patterns

### Feature Module Structure
```
src/app/features/users/
├── components/
│   ├── user-list/
│   └── user-form/
├── services/
│   └── user.service.ts
├── store/
│   ├── user.actions.ts
│   ├── user.reducer.ts
│   ├── user.selectors.ts
│   └── user.effects.ts
└── models/
    └── user.model.ts
```

### Dependency Injection
Use `@inject()` for cleaner DI:

```typescript
export class MyService {
  private http = inject(HttpClient);
  private store = inject(Store);
  
  // Instead of constructor injection
}
```

### Reactive Forms
```typescript
export class UserFormComponent {
  private fb = inject(FormBuilder);
  
  form = this.fb.group({
    name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]]
  });
  
  onSubmit() {
    if (this.form.valid) {
      // Handle form submission
    }
  }
}
```

## Testing Strategies

### Component Testing
```typescript
describe('UserComponent', () => {
  let component: UserComponent;
  let fixture: ComponentFixture<UserComponent>;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserComponent]
    });
    fixture = TestBed.createComponent(UserComponent);
    component = fixture.componentInstance;
  });
  
  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

### Service Testing
```typescript
describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should fetch users', () => {
    const mockUsers = [{ id: 1, name: 'John' }];
    
    service.getUsers().subscribe(users => {
      expect(users).toEqual(mockUsers);
    });
    
    const req = httpMock.expectOne('/api/users');
    req.flush(mockUsers);
  });
});
```

## Best Practices

1. **Use standalone components** for new features
2. **Prefer signals** for local component state
3. **Use NgRx** for complex global state
4. **Implement proper error handling** with try-catch and error boundaries
5. **Use data-testid** attributes for E2E testing
6. **Avoid any type** - use proper TypeScript typing
7. **Keep components focused** on single responsibility
8. **Use reactive forms** for complex form handling
