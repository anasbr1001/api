// api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000';
const authToken = btoa(`${process.env.REACT_APP_API_USER}:${process.env.REACT_APP_API_PASS}`);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Basic ${authToken}`
  }
});

// CRUD Operations
export const productApi = {
  // GET All Products
  getAll: async (page = 1, perPage = 10) => {
    try {
      const response = await api.get('/products', {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  // GET Single Product
  getById: async (id) => {
    try {
      const response = await api.get(`/products/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  },

  // POST Create Product
  create: async (productData) => {
    try {
      const response = await api.post('/products', productData);
      return response.data;
    } catch (error) {
      console.error('Error creating product:', error);
      throw error;
    }
  },

  // PUT Update Product
  update: async (id, updateData) => {
    try {
      const response = await api.put(`/products/${id}`, updateData);
      return response.data;
    } catch (error) {
      console.error(`Error updating product ${id}:`, error);
      throw error;
    }
  },

  // DELETE Product
  delete: async (id) => {
    try {
      const response = await api.delete(`/products/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting product ${id}:`, error);
      throw error;
    }
  },

  // Search Products
  search: async (query, limit = 20) => {
    try {
      const response = await api.get('/products/search', {
        params: { q: query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching products:', error);
      throw error;
    }
  }
};