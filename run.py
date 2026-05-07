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
    
    app.secret_key = os.environ.get('SECRET_KEY', 'ft_manager_secret_2024')
    
    # Base de datos — usa /data en Railway, local si no
    db_dir = os.environ.get('DB_PATH', os.path.dirname(__file__))
    app.config['DATABASE'] = os.path.join(db_dir, 'football.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'escudos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'fotos'), exist_ok=True)
    
    with app.app_context():
        init_db(app)
    
    register_blueprints(app)
    
    return app


# Al final de run.py
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("=" * 60)
    print("  FOOTBALL TOURNAMENT MANAGER")
    print(f"  Servidor: http://localhost:{port}")
    print("  Usuario: admin | Contraseña: admin123")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)
    
