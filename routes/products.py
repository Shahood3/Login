from flask import Blueprint, request, jsonify, g
from routes.auth import token_required
from models.product import Product
from bson import ObjectId

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products (public endpoint)"""
    try:
        is_active = request.args.get('is_active')
        category = request.args.get('category')
        location = request.args.get('location')  # NEW: Location filter
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))
        
        # Convert is_active to boolean
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        
        product_model = Product(g.mongo.db)
        result = product_model.get_all_products(is_active, category, location, skip, limit)
        
        return jsonify({
            'message': 'Products retrieved successfully',
            **result
        }), 200
        
    except Exception as e:
        print(f"Get products error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve products'}), 500

@products_bp.route('/locations', methods=['GET'])
def get_locations():
    """Get all unique locations (public endpoint)"""
    try:
        product_model = Product(g.mongo.db)
        locations = product_model.get_all_locations()
        
        return jsonify({
            'message': 'Locations retrieved successfully',
            'locations': locations
        }), 200
        
    except Exception as e:
        print(f"Get locations error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve locations'}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID (public endpoint)"""
    try:
        product_model = Product(g.mongo.db)
        product = product_model.get_product_by_id(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'message': 'Product retrieved successfully',
            'product': product
        }), 200
        
    except Exception as e:
        print(f"Get product error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve product'}), 500

@products_bp.route('', methods=['POST'])
@token_required
def create_product(current_user):
    """Create a new product (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'price_per_day', 'quantity_total']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        product_model = Product(g.mongo.db)
        result, status_code = product_model.create_product(data, current_user['_id'])
        
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"Create product error: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500

@products_bp.route('/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """Update product (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        product_model = Product(g.mongo.db)
        
        if product_model.update_product(product_id, data):
            updated_product = product_model.get_product_by_id(product_id)
            return jsonify({
                'message': 'Product updated successfully',
                'product': updated_product
            }), 200
        else:
            return jsonify({'error': 'Failed to update product'}), 500
            
    except Exception as e:
        print(f"Update product error: {str(e)}")
        return jsonify({'error': 'Failed to update product'}), 500

@products_bp.route('/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """Delete product (manager only)"""
    try:
        if current_user.get('user_type') != 'manager':
            return jsonify({'error': 'Access denied. Manager role required.'}), 403
        
        product_model = Product(g.mongo.db)
        
        if product_model.delete_product(product_id):
            return jsonify({'message': 'Product deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
            
    except Exception as e:
        print(f"Delete product error: {str(e)}")
        return jsonify({'error': 'Failed to delete product'}), 500