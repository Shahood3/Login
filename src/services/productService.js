const API_BASE_URL = 'http://localhost:8080/api';

export const productService = {
  getAllProducts: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
      if (filters.category) params.append('category', filters.category);
      if (filters.location) params.append('location', filters.location);  // NEW
      if (filters.skip) params.append('skip', filters.skip);
      if (filters.limit) params.append('limit', filters.limit);

      const response = await fetch(`${API_BASE_URL}/products?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch products');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  getLocations: async () => {  // NEW
    try {
      const response = await fetch(`${API_BASE_URL}/products/locations`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch locations');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  getProduct: async (productId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch product');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  createProduct: async (productData, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(productData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create product');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  updateProduct: async (productId, productData, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(productData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update product');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  deleteProduct: async (productId, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to delete product');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }
};