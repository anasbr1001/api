import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

interface JwtPayload {
  user_id: number;
  username: string;
  email: string;
  exp: number;
}

export const useAuth = create<AuthState>((set: any) => ({
  isAuthenticated: false,
  user: null,
  token: null,
  login: (token: string, user: User) => {
    localStorage.setItem('token', token);
    set({ isAuthenticated: true, user, token });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ isAuthenticated: false, user: null, token: null });
  },
}));

// Initialize auth state from localStorage
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const user = {
        id: decoded.user_id,
        username: decoded.username,
        email: decoded.email,
      };
      useAuth.getState().login(token, user);
    } catch (error) {
      localStorage.removeItem('token');
    }
  }
} 