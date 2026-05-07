"""
Football Tournament Manager - Main Application
Arquitectura: Flask + SQLite + Jinja2
"""
import os
from flask import Flask
from app.database import init_db
from app.routes import register_blueprints


def create_app():
    app = Flask(__name__, 
                template_folder='app/templates',
                static_folder='app/static')
    
    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', 'ft_manager_secret_2024')
    app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'football.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
    
    # Ensure upload directories exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'escudos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'fotos'), exist_ok=True)
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    # Register all blueprints
    register_blueprints(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("  FOOTBALL TOURNAMENT MANAGER")
    print("  Servidor iniciado en: http://localhost:5000")
    print("  Usuario: admin | Contraseña: admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
