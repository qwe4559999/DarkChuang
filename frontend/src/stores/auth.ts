import { writable } from 'svelte/store';

interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
}

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: User | null;
}

const initialState: AuthState = {
    isAuthenticated: false,
    token: null,
    user: null
};

// Load from localStorage if available
const storedToken = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
const storedUser = typeof localStorage !== 'undefined' ? localStorage.getItem('user') : null;

if (storedToken) {
    initialState.isAuthenticated = true;
    initialState.token = storedToken;
    initialState.user = storedUser ? JSON.parse(storedUser) : null;
}

export const auth = writable<AuthState>(initialState);

export const login = (token: string, user: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    auth.set({
        isAuthenticated: true,
        token,
        user
    });
};

export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    auth.set({
        isAuthenticated: false,
        token: null,
        user: null
    });
};
