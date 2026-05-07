"""
Routes - Blueprint registration for all modules.
"""
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.torneos import torneos_bp
from app.routes.equipos import equipos_bp
from app.routes.jugadores import jugadores_bp
from app.routes.partidos import partidos_bp
from app.routes.estadisticas import stats_bp
from app.routes.arbitros import arbitros_bp
from app.routes.usuarios import usuarios_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(torneos_bp, url_prefix='/torneos')
    app.register_blueprint(equipos_bp, url_prefix='/equipos')
    app.register_blueprint(jugadores_bp, url_prefix='/jugadores')
    app.register_blueprint(partidos_bp, url_prefix='/partidos')
    app.register_blueprint(stats_bp, url_prefix='/estadisticas')
    app.register_blueprint(arbitros_bp, url_prefix='/arbitros')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')