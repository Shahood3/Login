from datetime import datetime
from bson import ObjectId

class Rental:
    def __init__(self, db):
        self.collection = db.rentals
        
    def create_rental(self, rental_data):
        """Create a new rental booking"""
        try:
            # Convert user_id to ObjectId for storage
            user_id = rental_data['user_id']
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Convert product_id to ObjectId for storage
            product_id = rental_data['product_id']
            if isinstance(product_id, str):
                product_id = ObjectId(product_id)
            
            rental_doc = {
                'user_id': user_id,  # Store as ObjectId
                'product_id': product_id,  # Store as ObjectId
                'quantity': int(rental_data['quantity']),
                'start_date': datetime.fromisoformat(rental_data['start_date'].replace('Z', '+00:00')),
                'end_date': datetime.fromisoformat(rental_data['end_date'].replace('Z', '+00:00')),
                'total_days': rental_data['total_days'],
                'price_per_day': float(rental_data['price_per_day']),
                'total_price': float(rental_data['total_price']),
                'status': 'pending',  # pending, approved, active, completed, cancelled
                'payment_status': 'unpaid',  # unpaid, paid, refunded
                'notes': rental_data.get('notes', ''),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(rental_doc)
            
            if result.inserted_id:
                rental_doc['_id'] = str(result.inserted_id)
                rental_doc['user_id'] = str(rental_doc['user_id'])
                rental_doc['product_id'] = str(rental_doc['product_id'])
                return {
                    'message': 'Rental request created successfully',
                    'rental': rental_doc
                }, 201
            else:
                return {'error': 'Failed to create rental'}, 500
                
        except Exception as e:
            print(f"Error creating rental: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {'error': 'Internal server error'}, 500
    
    def _convert_rental_ids(self, rental):
        """Helper method to convert all ObjectIds in rental to strings"""
        if rental:
            rental['_id'] = str(rental['_id'])
            rental['user_id'] = str(rental['user_id'])
            rental['product_id'] = str(rental['product_id'])
            # Convert updated_by if it exists
            if 'updated_by' in rental and rental['updated_by']:
                rental['updated_by'] = str(rental['updated_by'])
        return rental
    
    def get_all_rentals(self, filters=None, skip=0, limit=50):
        """Get all rentals with optional filtering"""
        try:
            query = filters if filters else {}
            
            rentals = list(self.collection.find(query).skip(skip).limit(limit).sort('created_at', -1))
            for rental in rentals:
                self._convert_rental_ids(rental)
            
            total_count = self.collection.count_documents(query)
            
            return {
                'rentals': rentals,
                'total': total_count,
                'skip': skip,
                'limit': limit
            }
        except Exception as e:
            print(f"Error getting rentals: {str(e)}")
            return {'rentals': [], 'total': 0, 'skip': skip, 'limit': limit}
    
    def get_rental_by_id(self, rental_id):
        """Get rental by ID"""
        try:
            if isinstance(rental_id, str):
                object_id = ObjectId(rental_id)
            else:
                object_id = rental_id
                
            rental = self.collection.find_one({'_id': object_id})
            return self._convert_rental_ids(rental)
        except Exception as e:
            print(f"Error getting rental by ID: {str(e)}")
            return None
    
    def get_user_rentals(self, user_id, status=None):
        """Get all rentals for a specific user"""
        try:
            # Convert user_id to ObjectId for query
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            query = {'user_id': user_id}
            if status:
                query['status'] = status
            
            print(f"Querying rentals with: {query}")  # Debug log
            
            rentals = list(self.collection.find(query).sort('created_at', -1))
            
            print(f"Found {len(rentals)} rentals")  # Debug log
            
            for rental in rentals:
                self._convert_rental_ids(rental)
            
            return rentals
        except Exception as e:
            print(f"Error getting user rentals: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def update_rental_status(self, rental_id, status, updated_by=None):
        """Update rental status"""
        try:
            if isinstance(rental_id, str):
                object_id = ObjectId(rental_id)
            else:
                object_id = rental_id
                
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if updated_by:
                if isinstance(updated_by, str):
                    updated_by = ObjectId(updated_by)
                update_data['updated_by'] = updated_by
                
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': update_data}
            )
            
            print(f"Updated rental {rental_id} status to {status}: {result.modified_count} modified")  # Debug log
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating rental status: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def update_payment_status(self, rental_id, payment_status):
        """Update payment status"""
        try:
            if isinstance(rental_id, str):
                object_id = ObjectId(rental_id)
            else:
                object_id = rental_id
                
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': {
                    'payment_status': payment_status,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating payment status: {str(e)}")
            return False