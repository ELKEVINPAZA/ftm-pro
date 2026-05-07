"""Dashboard - main overview."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.routes.auth import login_required
from app.models import Torneo, TablaPosiciones, Partido
from app.database import query_db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    torneos = Torneo.get_all()
    torneo_activo = Torneo.get_activo()
    stats = {}
    tabla = []
    proximos = []
    goleadores = []

    if torneo_activo:
        stats = Torneo.get_stats(torneo_activo['id'])
        tabla = TablaPosiciones.calcular(torneo_activo['id'])[:5]
        proximos = Partido.get_all(torneo_activo['id'], 'pendiente')[:5]
        goleadores = TablaPosiciones.goleadores(torneo_activo['id'], 5)

    return render_template('dashboard/index.html',
                           torneos=torneos,
                           torneo_activo=torneo_activo,
                           stats=stats,
                           tabla=tabla,
                           proximos=proximos,
                           goleadores=goleadores)
