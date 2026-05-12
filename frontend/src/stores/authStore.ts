import { create } from 'zustand';
import type { User } from '../types/user';
import api from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  restoreSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: (token, user) => {
    localStorage.setItem('token', token);
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false });
  },

  restoreSession: () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    api.get('/auth/me').then(({ data }) => {
      set({ token, user: data, isAuthenticated: true });
    }).catch(() => {
      localStorage.removeItem('token');
    });
  },
}));
