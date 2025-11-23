const API_BASE_URL = 'http://localhost:8080/api';

export const rentalService = {
  createRental: async (rentalData, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/rentals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(rentalData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create rental');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  getAllRentals: async (filters, token) => {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.skip) params.append('skip', filters.skip);
      if (filters?.limit) params.append('limit', filters.limit);

      const response = await fetch(`${API_BASE_URL}/rentals?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch rentals');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  updateRentalStatus: async (rentalId, status, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/rentals/${rentalId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update rental status');
      }

      return data;
    } catch (error) {
      throw error;
    }
  },

  updatePaymentStatus: async (rentalId, paymentStatus, token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/rentals/${rentalId}/payment`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ payment_status: paymentStatus })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update payment status');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }
};