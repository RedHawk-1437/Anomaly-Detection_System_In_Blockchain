from flask import Flask
import os


def create_app():
    """Flask application factory"""
    # Templates folder ka absolute path set karen
    template_dir = os.path.abspath('templates')
    static_dir = os.path.abspath('static')

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    # Basic configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Services initialize karen
    from app.services.simblock_service import SimBlockService
    from app.services.attack_service import AttackService
    from app.services.ml_service import MLService

    # Create service instances
    simblock_service = SimBlockService()
    attack_service = AttackService(simblock_service)
    ml_service = MLService(simblock_service, attack_service)

    # Store services in app context
    app.config['simblock_service'] = simblock_service
    app.config['attack_service'] = attack_service
    app.config['ml_service'] = ml_service

    # Blueprints register keren
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.simblock_routes import simblock_bp
    from app.routes.attack_routes import attack_bp
    from app.routes.ml_routes import ml_bp
    from app.routes.kaggle_routes import kaggle_bp  # ✅ NEW

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(simblock_bp)
    app.register_blueprint(attack_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(kaggle_bp)  # ✅ NEW

    # Create necessary directories
    create_directories()

    print("✅ Flask app successfully configured with ML System & Kaggle Integration!")
    return app


def create_directories():
    """Required directories create keren - FIXED VERSION"""
    directories = [
        'data',
        'data/kaggle_datasets',
        'data/processed_datasets',
        'static',
        'templates',
        'ml_training'
    ]

    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"📁 Created directory: {directory}")
        except Exception as e:
            print(f"⚠️ Error creating directory {directory}: {e}")