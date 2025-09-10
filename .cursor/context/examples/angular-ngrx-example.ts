// NgRx implementation example with Angular 20
import { Component, inject, signal } from '@angular/core';
import { Store } from '@ngrx/store';
import { User } from './models/user.model';
import { loadUser, updateUser } from './store/user.actions';
import { selectLoading, selectUser } from './store/user.selectors';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  template: `
    <div data-testid="user-profile">
      @if (loading()) {
        <div data-testid="loading">Loading...</div>
      } @else {
        <div data-testid="user-info">
          <h2>{{ user()?.name }}</h2>
          <p>{{ user()?.email }}</p>
        </div>
      }
    </div>
  `
})
export class UserProfileComponent {
  private store = inject(Store);
  
  // Usando signals para estado local
  user = signal<User | null>(null);
  loading = signal(false);
  
  // Selectores NgRx
  user$ = this.store.select(selectUser);
  loading$ = this.store.select(selectLoading);
  
  ngOnInit() {
    this.store.dispatch(loadUser());
    
    // Suscripción a cambios
    this.user$.subscribe(user => this.user.set(user));
    this.loading$.subscribe(loading => this.loading.set(loading));
  }
  
  updateUser(userData: Partial<User>) {
    this.store.dispatch(updateUser({ user: userData }));
  }
}
