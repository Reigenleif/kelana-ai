import api from './api';

export const authService = {
  async login(usernameOrEmail, password) {
    const response = await api.post('/auth/login', {
      username_or_email: usernameOrEmail,
      password,
    });
    if (response.data?.access_token) {
      localStorage.setItem('kelana_token', response.data.access_token);
      localStorage.setItem('kelana_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    if (response.data?.access_token) {
      localStorage.setItem('kelana_token', response.data.access_token);
      localStorage.setItem('kelana_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async getMe() {
    const response = await api.get('/auth/me');
    if (response.data) {
      localStorage.setItem('kelana_user', JSON.stringify(response.data));
    }
    return response.data;
  },

  async getUsers() {
    const response = await api.get('/users');
    return response.data;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('kelana_token');
      localStorage.removeItem('kelana_user');
    }
  },

  getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('kelana_token');
    }
    return null;
  },

  getCurrentUser() {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('kelana_user');
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch {
          return null;
        }
      }
    }
    return null;
  },

  isAuthenticated() {
    return !!this.getToken();
  },
};

export default authService;
