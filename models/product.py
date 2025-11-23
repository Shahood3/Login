from datetime import datetime
from bson import ObjectId

class Product:
    def __init__(self, db):
        self.collection = db.products
        
    def create_product(self, product_data, manager_id):
        """Create a new product"""
        try:
            product_doc = {
                'name': product_data['name'].strip(),
                'description': product_data.get('description', '').strip(),
                'category': product_data.get('category', 'general').strip(),
                'location': product_data.get('location', '').strip(),  # NEW: Location field
                'price_per_day': float(product_data['price_per_day']),
                'quantity_total': int(product_data['quantity_total']),
                'quantity_available': int(product_data['quantity_total']),
                'image_url': product_data.get('image_url', ''),
                'specifications': product_data.get('specifications', {}),
                'is_active': True,
                'added_by': manager_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(product_doc)
            
            if result.inserted_id:
                product_doc['_id'] = str(result.inserted_id)
                return {
                    'message': 'Product added successfully',
                    'product': product_doc
                }, 201
            else:
                return {'error': 'Failed to add product'}, 500
                
        except Exception as e:
            print(f"Error creating product: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def get_all_products(self, is_active=None, category=None, location=None, skip=0, limit=50):
        """Get all products with optional filtering"""
        try:
            query = {}
            if is_active is not None:
                query['is_active'] = is_active
            if category:
                query['category'] = category
            if location:  # NEW: Location filter
                query['location'] = location
            
            products = list(self.collection.find(query).skip(skip).limit(limit).sort('created_at', -1))
            for product in products:
                product['_id'] = str(product['_id'])
                product['added_by'] = str(product['added_by'])
            
            total_count = self.collection.count_documents(query)
            
            return {
                'products': products,
                'total': total_count,
                'skip': skip,
                'limit': limit
            }
        except Exception as e:
            print(f"Error getting products: {str(e)}")
            return {'products': [], 'total': 0, 'skip': skip, 'limit': limit}
    
    def get_all_locations(self):
        """Get list of all unique locations"""
        try:
            locations = self.collection.distinct('location', {'is_active': True, 'location': {'$ne': ''}})
            return sorted(locations)
        except Exception as e:
            print(f"Error getting locations: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        try:
            if isinstance(product_id, str):
                object_id = ObjectId(product_id)
            else:
                object_id = product_id
                
            product = self.collection.find_one({'_id': object_id})
            if product:
                product['_id'] = str(product['_id'])
                product['added_by'] = str(product['added_by'])
            return product
        except Exception as e:
            print(f"Error getting product by ID: {str(e)}")
            return None
    
    def update_product(self, product_id, update_data):
        """Update product information"""
        try:
            if isinstance(product_id, str):
                object_id = ObjectId(product_id)
            else:
                object_id = product_id
                
            # Remove fields that shouldn't be updated directly
            update_data.pop('_id', None)
            update_data.pop('created_at', None)
            update_data.pop('added_by', None)
            update_data.pop('quantity_available', None)  # Managed by rental system
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return False
    
    def update_quantity(self, product_id, quantity_change):
        """Update available quantity (used by rental system)"""
        try:
            if isinstance(product_id, str):
                object_id = ObjectId(product_id)
            else:
                object_id = product_id
                
            result = self.collection.update_one(
                {'_id': object_id},
                {
                    '$inc': {'quantity_available': quantity_change},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating quantity: {str(e)}")
            return False
    
    def delete_product(self, product_id):
        """Soft delete product (set is_active to False)"""
        try:
            if isinstance(product_id, str):
                object_id = ObjectId(product_id)
            else:
                object_id = product_id
                
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False