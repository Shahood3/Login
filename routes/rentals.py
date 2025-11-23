from flask import Blueprint, request, jsonify, g
from routes.auth import token_required
from models.rental import Rental
from models.product import Product
from bson import ObjectId
from datetime import datetime

rentals_bp = Blueprint('rentals', __name__, url_prefix='/api/rentals')

@rentals_bp.route('', methods=['POST'])
@token_required
def create_rental(current_user):
    """Create a new rental booking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['product_id', 'quantity', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Get product details
        product_model = Product(g.mongo.db)
        product = product_model.get_product_by_id(data['product_id'])
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if not product['is_active']:
            return jsonify({'error': 'Product is not available'}), 400
        
        # Check quantity availability
        if int(data['quantity']) > product['quantity_available']:
            return jsonify({
                'error': f'Only {product["quantity_available"]} units available'
            }), 400
        
        # Calculate dates and price
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        total_days = (end_date - start_date).days + 1
        
        if total_days < 1:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        # Use current_user['_id'] which is already a string
        rental_data = {
            'user_id': current_user['_id'],  # Pass as string, will be converted to ObjectId in model
            'product_id': data['product_id'],
            'quantity': data['quantity'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'total_days': total_days,
            'price_per_day': product['price_per_day'],
            'total_price': product['price_per_day'] * total_days * int(data['quantity']),
            'notes': data.get('notes', '')
        }
        
        rental_model = Rental(g.mongo.db)
        result, status_code = rental_model.create_rental(rental_data)
        
        # Update product quantity
        if status_code == 201:
            product_model.update_quantity(data['product_id'], -int(data['quantity']))
        
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"Create rental error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to create rental'}), 500

@rentals_bp.route('', methods=['GET'])
@token_required
def get_rentals(current_user):
    """Get rentals (all for manager, own for user)"""
    try:
        rental_model = Rental(g.mongo.db)
        
        if current_user.get('user_type') == 'manager':
            # Manager can see all rentals
            status = request.args.get('status')
            skip = int(request.args.get('skip', 0))
            limit = int(request.args.get('limit', 50))
            
            filters = {}
            if status:
                filters['status'] = status
            
            result = rental_model.get_all_rentals(filters, skip, limit)
            
            # Populate product and user details
            from models.user import User
            product_model = Product(g.mongo.db)
            user_model = User(g.mongo.db)
            
            for rental in result['rentals']:
                product = product_model.get_product_by_id(rental['product_id'])
                user = user_model.get_user_by_id(rental['user_id'])
                rental['product'] = product
                rental['user'] = user
            
            return jsonify({
                'message': 'Rentals retrieved successfully',
                **result
            }), 200
        else:
            # Regular user can only see their rentals
            status = request.args.get('status')
            
            print(f"Fetching rentals for user: {current_user['_id']}")  # Debug log
            
            rentals = rental_model.get_user_rentals(current_user['_id'], status)
            
            print(f"Retrieved {len(rentals)} rentals for user")  # Debug log
            
            # Populate product details
            product_model = Product(g.mongo.db)
            for rental in rentals:
                product = product_model.get_product_by_id(rental['product_id'])
                rental['product'] = product
            
            return jsonify({
                'message': 'Rentals retrieved successfully',
                'rentals': rentals,
                'total': len(rentals)
            }), 200
        
    except Exception as e:
        print(f"Get rentals error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to retrieve rentals'}), 500

@rentals_bp.route('/<rental_id>', methods=['GET'])
@token_required
def get_rental(current_user, rental_id):
    """Get rental by ID"""
    try:
        rental_model = Rental(g.mongo.db)
        rental = rental_model.get_rental_by_id(rental_id)
        
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404
        
        # Check access
        if current_user.get('user_type') != 'manager' and rental['user_id'] != current_user['_id']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Populate details
        product_model = Product(g.mongo.db)
        rental['product'] = product_model.get_product_by_id(rental['product_id'])
        
        if current_user.get('user_type') == 'manager':
            from models.user import User
            user_model = User(g.mongo.db)
            rental['user'] = user_model.get_user_by_id(rental['user_id'])
        
        return jsonify({
            'message': 'Rental retrieved successfully',
            'rental': rental
        }), 200
        
    except Exception as e:
        print(f"Get rental error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve rental'}), 500

@rentals_bp.route('/<rental_id>/status', methods=['PUT'])
@token_required
def update_rental_status(current_user, rental_id):
    """Update rental status (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'approved', 'active', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        rental_model = Rental(g.mongo.db)
        rental = rental_model.get_rental_by_id(rental_id)
        
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404
        
        old_status = rental['status']
        new_status = data['status']
        
        print(f"Updating rental {rental_id} from {old_status} to {new_status}")  # Debug log
        
        # If cancelling or rejecting, return quantity to product
        if new_status in ['cancelled'] and old_status in ['pending', 'approved']:
            product_model = Product(g.mongo.db)
            product_model.update_quantity(rental['product_id'], rental['quantity'])
        
        # If completing, return quantity to product
        if new_status == 'completed' and old_status == 'active':
            product_model = Product(g.mongo.db)
            product_model.update_quantity(rental['product_id'], rental['quantity'])
        
        if rental_model.update_rental_status(rental_id, new_status, current_user['_id']):
            updated_rental = rental_model.get_rental_by_id(rental_id)
            
            # Populate product details
            product_model = Product(g.mongo.db)
            updated_rental['product'] = product_model.get_product_by_id(updated_rental['product_id'])
            
            return jsonify({
                'message': 'Rental status updated successfully',
                'rental': updated_rental
            }), 200
        else:
            return jsonify({'error': 'Failed to update rental status'}), 500
            
    except Exception as e:
        print(f"Update rental status error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to update rental status'}), 500

@rentals_bp.route('/<rental_id>/payment', methods=['PUT'])
@token_required
def update_payment_status(current_user, rental_id):
    """Update payment status (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        data = request.get_json()
        
        if not data or 'payment_status' not in data:
            return jsonify({'error': 'Payment status is required'}), 400
        
        valid_statuses = ['unpaid', 'paid', 'refunded']
        if data['payment_status'] not in valid_statuses:
            return jsonify({'error': 'Invalid payment status'}), 400
        
        rental_model = Rental(g.mongo.db)
        
        if rental_model.update_payment_status(rental_id, data['payment_status']):
            updated_rental = rental_model.get_rental_by_id(rental_id)
            return jsonify({
                'message': 'Payment status updated successfully',
                'rental': updated_rental
            }), 200
        else:
            return jsonify({'error': 'Failed to update payment status'}), 500
            
    except Exception as e:
        print(f"Update payment status error: {str(e)}")
        return jsonify({'error': 'Failed to update payment status'}), 500