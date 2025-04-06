import os
import logging
from flask import Flask, send_from_directory
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Path to your React build (Vite output is usually in client/dist)
    react_build_dir = os.path.join(base_dir, '../client/dist')
    
    app = Flask(__name__, static_folder=react_build_dir, static_url_path='/')
    app.config.from_object(Config)
    
    # Enable CORS for all routes (for development, you might restrict this in production)
    CORS(app)  # This will allow requests from any origin

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s')
    logging.info("Starting AlertBySyncgram backend...")
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register API Blueprints
    from routes.owner import owner_bp
    from routes.subscriber import subscriber_bp
    from routes.paystack import paystack_bp
    from routes.twilio import twilio_bp
    from routes.alerts import alerts_bp

    app.register_blueprint(owner_bp, url_prefix='/api/owner')
    app.register_blueprint(subscriber_bp, url_prefix='/api/subscriber')
    app.register_blueprint(paystack_bp, url_prefix='/api/paystack')
    app.register_blueprint(twilio_bp, url_prefix='/api/twilio')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    
    # Catch-all route for serving the React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app
