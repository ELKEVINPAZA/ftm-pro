"""Estadisticas routes."""
from flask import Blueprint, render_template, request
from app.routes.auth import login_required
from app.models import TablaPosiciones, Torneo, Partido

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/')
@login_required
def index():
    torneo_id = request.args.get('torneo_id', type=int)
    torneos = Torneo.get_all()
    tabla = []
    goleadores = []
    fair_play = []
    torneo = None

    if torneo_id:
        torneo = Torneo.get_by_id(torneo_id)
        tabla = TablaPosiciones.calcular(torneo_id)
        goleadores = TablaPosiciones.goleadores(torneo_id, 15)
        fair_play = TablaPosiciones.fair_play(torneo_id)
    elif torneos:
        torneo_id = torneos[0]['id']
        torneo = torneos[0]
        tabla = TablaPosiciones.calcular(torneo_id)
        goleadores = TablaPosiciones.goleadores(torneo_id, 15)
        fair_play = TablaPosiciones.fair_play(torneo_id)

    return render_template('estadisticas/index.html',
                           torneos=torneos, torneo=torneo,
                           torneo_id=torneo_id, tabla=tabla,
                           goleadores=goleadores, fair_play=fair_play)
