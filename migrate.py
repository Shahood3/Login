from pymongo import MongoClient
from bson import ObjectId
from config import Config

def migrate_rentals():
    """Migrate existing rental user_ids and product_ids from string to ObjectId"""
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DB_NAME]
    rentals_collection = db.rentals
    
    print("Starting rental migration...")
    
    # Find all rentals
    rentals = rentals_collection.find({})
    updated_count = 0
    
    for rental in rentals:
        update_needed = False
        update_data = {}
        
        # Check and convert user_id
        if isinstance(rental.get('user_id'), str):
            try:
                update_data['user_id'] = ObjectId(rental['user_id'])
                update_needed = True
            except Exception as e:
                print(f"Error converting user_id for rental {rental['_id']}: {e}")
        
        # Check and convert product_id
        if isinstance(rental.get('product_id'), str):
            try:
                update_data['product_id'] = ObjectId(rental['product_id'])
                update_needed = True
            except Exception as e:
                print(f"Error converting product_id for rental {rental['_id']}: {e}")
        
        # Update if needed
        if update_needed:
            rentals_collection.update_one(
                {'_id': rental['_id']},
                {'$set': update_data}
            )
            updated_count += 1
            print(f"Updated rental {rental['_id']}")
    
    print(f"Migration completed. Updated {updated_count} rentals.")
    client.close()

if __name__ == '__main__':
    migrate_rentals()