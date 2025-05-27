const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

interface Product {
  id?: string;
  title: string;
  price: number;
  [key: string]: any;
}

const handleResponse = async (response: Response): Promise<any> => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: `HTTP error! status: ${response.status}`
    }));
    throw new Error(errorData.message || 'Request failed');
  }
  return response.json();
};

const fetchApi = async (endpoint: string, method: string = 'GET', body: object | null = null) => {
  try {
    const response = await fetch(`/api${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : null
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};

export const productApi = {
  getAll: async (page: number = 1, perPage: number = 10): Promise<{products: Product[], total: number}> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    });
    return fetchApi(`/products?${params}`);
  },

  getById: async (id: string): Promise<Product> => {
    if (!id) throw new Error('Product ID is required');
    return fetchApi(`/products/${id}`);
  },

  create: async (productData: Product): Promise<Product> => {
    if (!productData?.title) throw new Error('Product title is required');
    return fetchApi('/products', 'POST', productData);
  },

  update: async (id: string, updateData: Partial<Product>): Promise<Product> => {
    if (!id) throw new Error('Product ID is required');
    return fetchApi(`/products/${id}`, 'PUT', updateData);
  },

  delete: async (id: string): Promise<void> => {
    if (!id) throw new Error('Product ID is required');
    await fetchApi(`/products/${id}`, 'DELETE');
  }
};