import React, { useState, useEffect } from 'react';
import ProductList from './ProductList';
import AddProduct from './AddProduct';
import RentalList from './RentalList';
import { productService } from '../services/productService';
import { rentalService } from '../services/rentalService';

const Dashboard = ({ currentUser, onLogout }) => {
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [rentals, setRentals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  
  // NEW: Filter states
  const [filters, setFilters] = useState({
    category: '',
    location: ''
  });
  const [locations, setLocations] = useState([]);

  const isManager = currentUser?.user_type === 'manager';

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    if (activeTab === 'products') {
      loadProducts();
    } else if (activeTab === 'rentals') {
      loadRentals();
    }
  }, [activeTab, filters]);

  const loadLocations = async () => {
    try {
      const data = await productService.getLocations();
      setLocations(data.locations || []);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    try {
      const filterParams = {
        is_active: true,
        ...(filters.category && { category: filters.category }),
        ...(filters.location && { location: filters.location })
      };
      const data = await productService.getAllProducts(filterParams);
      setProducts(data.products || []);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRentals = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const data = await rentalService.getAllRentals({}, token);
      setRentals(data.rentals || []);
    } catch (error) {
      console.error('Error loading rentals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProductAdded = () => {
    setShowAddProduct(false);
    loadProducts();
    loadLocations(); // Refresh locations
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      category: '',
      location: ''
    });
  };

  const categories = ['camera', 'lighting', 'audio', 'backdrop', 'props', 'other'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Studio Rental Dashboard</h1>
              <p className="mt-1 text-sm text-gray-500">
                Welcome, {currentUser?.first_name} {currentUser?.last_name}
                {isManager && <span className="ml-2 text-blue-600 font-semibold">(Manager)</span>}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('products')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'products'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Products
            </button>
            <button
              onClick={() => setActiveTab('rentals')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'rentals'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {isManager ? 'All Rentals' : 'My Rentals'}
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'products' && (
          <div>
            {/* Filters and Add Button Section */}
            <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              {/* Filters */}
              <div className="flex flex-wrap gap-3 items-center">
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Categories</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>

                <select
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Locations</option>
                  {locations.map(loc => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))}
                </select>

                {(filters.category || filters.location) && (
                  <button
                    onClick={clearFilters}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 underline"
                  >
                    Clear Filters
                  </button>
                )}
              </div>

              {/* Add Product Button */}
              {isManager && (
                <button
                  onClick={() => setShowAddProduct(!showAddProduct)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 whitespace-nowrap"
                >
                  {showAddProduct ? 'Cancel' : 'Add New Product'}
                </button>
              )}
            </div>

            {showAddProduct && (
              <div className="mb-8">
                <AddProduct onProductAdded={handleProductAdded} />
              </div>
            )}

            <ProductList
              products={products}
              loading={loading}
              isManager={isManager}
              onProductUpdated={loadProducts}
              currentUser={currentUser}
            />
          </div>
        )}

        {activeTab === 'rentals' && (
          <RentalList
            rentals={rentals}
            loading={loading}
            isManager={isManager}
            onRentalUpdated={loadRentals}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;