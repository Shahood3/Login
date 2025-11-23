import React from 'react';
import { rentalService } from '../services/rentalService';

const RentalList = ({ rentals, loading, isManager, onRentalUpdated }) => {
  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      active: 'bg-green-100 text-green-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPaymentColor = (status) => {
    const colors = {
      unpaid: 'bg-red-100 text-red-800',
      paid: 'bg-green-100 text-green-800',
      refunded: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const handleStatusUpdate = async (rentalId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await rentalService.updateRentalStatus(rentalId, newStatus, token);
      onRentalUpdated();
    } catch (error) {
      alert('Failed to update status: ' + error.message);
    }
  };

  const handlePaymentUpdate = async (rentalId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await rentalService.updatePaymentStatus(rentalId, newStatus, token);
      onRentalUpdated();
    } catch (error) {
      alert('Failed to update payment: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">Loading rentals...</div>
      </div>
    );
  }

  if (rentals.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-500">No rentals found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {rentals.map((rental) => (
        <div key={rental._id} className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {rental.product?.name || 'Product'}
              </h3>
              {isManager && rental.user && (
                <p className="text-sm text-gray-600">
                  Customer: {rental.user.first_name} {rental.user.last_name} ({rental.user.email})
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <span className={`px-3 py-1 text-xs font-semibold rounded ${getStatusColor(rental.status)}`}>
                {rental.status.toUpperCase()}
              </span>
              <span className={`px-3 py-1 text-xs font-semibold rounded ${getPaymentColor(rental.payment_status)}`}>
                {rental.payment_status.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-500">Quantity</p>
              <p className="font-semibold">{rental.quantity} units</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Start Date</p>
              <p className="font-semibold">
                {new Date(rental.start_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">End Date</p>
              <p className="font-semibold">
                {new Date(rental.end_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Total Price</p>
              <p className="font-semibold text-blue-600">₹{rental.total_price}</p>
            </div>
          </div>

          {rental.notes && (
            <div className="mb-4">
              <p className="text-xs text-gray-500">Notes</p>
              <p className="text-sm">{rental.notes}</p>
            </div>
          )}

          {isManager && (
            <div className="flex gap-2 flex-wrap">
              {rental.status === 'pending' && (
                <>
                  <button
                    onClick={() => handleStatusUpdate(rental._id, 'approved')}
                    className="px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(rental._id, 'cancelled')}
                    className="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
                  >
                    Reject
                  </button>
                </>
              )}

              {rental.status === 'approved' && (
                <button
                  onClick={() => handleStatusUpdate(rental._id, 'active')}
                  className="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                >
                  Mark as Active
                </button>
              )}

              {rental.status === 'active' && (
                <button
                  onClick={() => handleStatusUpdate(rental._id, 'completed')}
                  className="px-4 py-2 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
                >
                  Complete Rental
                </button>
              )}

              {rental.payment_status === 'unpaid' && (
                <button
                  onClick={() => handlePaymentUpdate(rental._id, 'paid')}
                  className="px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                >
                  Mark as Paid
                </button>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default RentalList;