/**
 * Authentication service with secure backend integration.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface SignupRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  name?: string;
}

/**
 * Sign up a new user.
 */
export async function signup(request: SignupRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  const data: AuthResponse = await response.json();

  // Store auth data
  localStorage.setItem('auth_token', data.access_token);
  localStorage.setItem('user_id', data.user_id);

  return data;
}

/**
 * Login an existing user.
 */
export async function login(request: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data: AuthResponse = await response.json();

  // Store auth data
  localStorage.setItem('auth_token', data.access_token);
  localStorage.setItem('user_id', data.user_id);

  return data;
}

/**
 * Create a test user and get a JWT token (for quick demo).
 * For development/demo purposes only.
 */
export async function devLogin(): Promise<string> {
  // Generate random credentials for demo mode
  const randomEmail = `demo-${Date.now()}@example.com`;
  const randomPassword = `demo${Date.now()}`;

  try {
    // Try to signup with random credentials
    const response = await signup({
      email: randomEmail,
      password: randomPassword,
      name: 'Demo User',
    });

    return response.access_token;
  } catch (error) {
    console.error('Demo login failed:', error);
    throw error;
  }
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('auth_token');
  const userId = localStorage.getItem('user_id');

  // Both token and user ID must exist for valid authentication
  return !!(token && userId);
}

/**
 * Clear all authentication data (for logout or fresh start).
 */
export function clearAuth(): void {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('test_user_id');
  localStorage.removeItem('current_conversation_id');
  localStorage.removeItem('current_conversation_messages');
}

/**
 * Logout user.
 */
export function logout(): void {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('current_conversation_id');
  localStorage.removeItem('current_conversation_messages');
}

/**
 * Get current user ID.
 */
export function getUserId(): string | null {
  return localStorage.getItem('user_id');
}
