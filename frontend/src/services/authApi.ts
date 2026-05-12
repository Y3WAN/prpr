import api from './api';
import type { User } from '../types/user';

export const authApi = {
  signup: (data: { email: string; password: string; nickname: string; role: string }) =>
    api.post<User>('/auth/signup', data),

  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; token_type: string; user: User }>('/auth/login', data),

  me: () => api.get<User>('/auth/me'),
};
