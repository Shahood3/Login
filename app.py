from flask import Flask, g
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'login')
    app.config['PORT'] = int(os.getenv('PORT', 8080))
    
    # Validate SECRET_KEY
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY must be set in environment variables")
    
    # CORS Configuration
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # MongoDB Client (singleton)
    mongo_client = MongoClient(app.config['MONGO_URI'])
    
    @app.before_request
    def before_request():
        """Set up database connection before each request"""
        if not hasattr(g, 'mongo'):
            g.mongo = type('obj', (object,), {
                'db': mongo_client[app.config['DB_NAME']]
            })()
    
    @app.teardown_appcontext
    def teardown_db(exception=None):
        """Clean up database connection"""
        mongo = g.pop('mongo', None)
        # Connection pooling handles cleanup automatically
    
    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Test database connection
            mongo_client.admin.command('ping')
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'Flask Authentication API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth/*'
            }
        }, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',port=8080,debug=True)