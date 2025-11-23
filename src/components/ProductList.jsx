import React, { useState } from 'react';
import RentProduct from './RentProduct';
import { productService } from '../services/productService';

const ProductList = ({ products, loading, isManager, onProductUpdated, currentUser }) => {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showRentModal, setShowRentModal] = useState(false);

  const handleRent = (product) => {
    setSelectedProduct(product);
    setShowRentModal(true);
  };

  const handleRentSuccess = () => {
    setShowRentModal(false);
    setSelectedProduct(null);
    onProductUpdated();
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      const token = localStorage.getItem('token');
      await productService.deleteProduct(productId, token);
      onProductUpdated();
    } catch (error) {
      alert('Failed to delete product: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">Loading products...</div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-500">No products available</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <div key={product._id} className="bg-white rounded-lg shadow overflow-hidden">
            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
                <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded">
                  {product.category}
                </span>
              </div>

              {/* NEW: Location Display */}
              {product.location && (
                <div className="flex items-center text-sm text-gray-600 mb-2">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {product.location}
                </div>
              )}

              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {product.description || 'No description'}
              </p>

              <div className="flex justify-between items-center mb-3">
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{product.price_per_day}
                  </p>
                  <p className="text-xs text-gray-500">per day</p>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-semibold ${
                    product.quantity_available > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {product.quantity_available > 0 ? 'Available' : 'Out of Stock'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {product.quantity_available} / {product.quantity_total} units
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                {!isManager && product.quantity_available > 0 && (
                  <button
                    onClick={() => handleRent(product)}
                    className="flex-1 bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
                  >
                    Rent Now
                  </button>
                )}

                {isManager && (
                  <>
                    <button
                      onClick={() => handleDelete(product._id)}
                      className="flex-1 bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {showRentModal && selectedProduct && (
        <RentProduct
          product={selectedProduct}
          onClose={() => setShowRentModal(false)}
          onSuccess={handleRentSuccess}
          currentUser={currentUser}
        />
      )}
    </>
  );
};

export default ProductList;