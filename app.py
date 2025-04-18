# app.py
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    react_build_dir = os.path.join(base_dir, '../client/dist')
    app = Flask(__name__, static_folder=react_build_dir, static_url_path='/')
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s')
    logging.info("Starting AlertBySyncgram backend...")

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from routes.owner import owner_bp
    from routes.subscriber import subscriber_bp
    from routes.paystack import paystack_bp
    from routes.twilio import twilio_bp
    from routes.alerts import alerts_bp
    from routes.telegram_bot import telegram_bp
    from routes.kora import kora_bp

    app.register_blueprint(owner_bp, url_prefix='/api/owner')
    app.register_blueprint(subscriber_bp, url_prefix='/api/subscriber')
    app.register_blueprint(paystack_bp, url_prefix='/api/paystack')
    app.register_blueprint(kora_bp, url_prefix='/api/korapay')
    app.register_blueprint(twilio_bp, url_prefix='/api/twilio')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(telegram_bp, url_prefix='/telegram')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)