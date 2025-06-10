import { jwtDecode } from 'jwt-decode';
import { Product } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

const checkTokenExpiration = (token: string): boolean => {
  try {
    const decoded = jwtDecode(token);
    return decoded.exp ? decoded.exp * 1000 > Date.now() : false;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return false;
  }
};

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('token');
  if (!token || !checkTokenExpiration(token)) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    return {};
  }
  return { Authorization: `Bearer ${token}` };
};

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

class ProductApi {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, { 
      ...options, 
      headers,
      credentials: 'include'
    });
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'An error occurred');
    }

    return response.json();
  }

  async getAll(page: number = 1, perPage: number = 10) {
    return this.fetchWithAuth(`${this.baseUrl}/products?page=${page}&per_page=${perPage}`);
  }

  async getById(id: string | number) {
    return this.fetchWithAuth(`${this.baseUrl}/products/${id}`);
  }

  async create(product: Omit<Product, 'id'>) {
    return this.fetchWithAuth(`${this.baseUrl}/products`, {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async update(id: string | number, product: Partial<Product>) {
    return this.fetchWithAuth(`${this.baseUrl}/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(product),
    });
  }

  async delete(id: string | number) {
    return this.fetchWithAuth(`${this.baseUrl}/products/${id}`, {
      method: 'DELETE',
    });
  }

  async search(query: string) {
    return this.fetchWithAuth(`${this.baseUrl}/products/search?q=${encodeURIComponent(query)}`);
  }
}

export const productApi = new ProductApi(API_BASE_URL);

export const productApiLegacy = {
  getAll: async (page = 1, perPage = 10) => {
    const response = await fetch(`${API_BASE_URL}/products?page=${page}&per_page=${perPage}`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch products');
    return response.json();
  },

  getById: async (id: string | number) => {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch product');
    return response.json();
  },

  create: async (product: Omit<Product, 'id'>) => {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(product),
    });
    if (!response.ok) throw new Error('Failed to create product');
    return response.json();
  },

  update: async (id: string | number, product: Partial<Product>) => {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(product),
    });
    if (!response.ok) throw new Error('Failed to update product');
    return response.json();
  },

  delete: async (id: string | number) => {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete product');
    return response.json();
  },

  search: async (query: string) => {
    const response = await fetch(`${API_BASE_URL}/products/search?q=${encodeURIComponent(query)}`, {
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to search products');
    return response.json();
  },
};