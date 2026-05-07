"""Partidos routes: CRUD + live result management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.routes.auth import login_required, admin_required, arbitro_required
from app.models import Partido, Equipo, Jugador, Arbitro, Torneo, TablaPosiciones
from app.database import query_db

partidos_bp = Blueprint('partidos', __name__)


@partidos_bp.route('/')
@login_required
def index():
    torneo_id = request.args.get('torneo_id', type=int)
    estado = request.args.get('estado')
    partidos = Partido.get_all(torneo_id, estado)
    torneos = Torneo.get_all()
    return render_template('partidos/index.html', partidos=partidos,
                           torneos=torneos, torneo_id=torneo_id,
                           estado_filtro=estado)


@partidos_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    torneos = Torneo.get_all()
    equipos = Equipo.get_all()
    arbitros = Arbitro.get_all()
    if request.method == 'POST':
        data = {
            'torneo_id': request.form['torneo_id'],
            'equipo_local_id': request.form['equipo_local_id'],
            'equipo_visitante_id': request.form['equipo_visitante_id'],
            'arbitro_id': request.form.get('arbitro_id') or None,
            'fecha': request.form.get('fecha', ''),
            'cancha': request.form.get('cancha', ''),
            'estado': 'pendiente',
        }
        if data['equipo_local_id'] == data['equipo_visitante_id']:
            flash('Los equipos no pueden ser iguales', 'danger')
        else:
            pid = Partido.create(data)
            flash('Partido creado', 'success')
            return redirect(url_for('partidos.detalle', pid=pid))
    return render_template('partidos/form.html', torneos=torneos,
                           equipos=equipos, arbitros=arbitros)


@partidos_bp.route('/<int:pid>')
@login_required
def detalle(pid):
    partido = Partido.get_by_id(pid)
    if not partido:
        flash('Partido no encontrado', 'danger')
        return redirect(url_for('partidos.index'))
    goles = Partido.get_goles(pid)
    tarjetas = Partido.get_tarjetas(pid)
    jugadores_local = Jugador.get_by_equipo(partido['equipo_local_id'])
    jugadores_visitante = Jugador.get_by_equipo(partido['equipo_visitante_id'])
    arbitros = Arbitro.get_all()
    return render_template('partidos/detalle.html',
                           partido=partido, goles=goles, tarjetas=tarjetas,
                           jugadores_local=jugadores_local,
                           jugadores_visitante=jugadores_visitante,
                           arbitros=arbitros)


@partidos_bp.route('/<int:pid>/resultado', methods=['POST'])
@arbitro_required
def actualizar_resultado(pid):
    goles_local = int(request.form.get('goles_local', 0))
    goles_visitante = int(request.form.get('goles_visitante', 0))
    estado = request.form.get('estado', 'finalizado')
    Partido.update_resultado(pid, goles_local, goles_visitante, estado)
    flash('Resultado actualizado', 'success')
    return redirect(url_for('partidos.detalle', pid=pid))


@partidos_bp.route('/<int:pid>/gol', methods=['POST'])
@arbitro_required
def agregar_gol(pid):
    partido = Partido.get_by_id(pid)
    Partido.registrar_gol(
        pid,
        request.form['jugador_id'],
        request.form['equipo_id'],
        request.form.get('minuto', 0),
        request.form.get('tipo', 'normal')
    )
    # Recalculate score
    goles = Partido.get_goles(pid)
    gl = sum(1 for g in goles if g['equipo_id'] == partido['equipo_local_id'] and g['tipo'] != 'autogol')
    gl += sum(1 for g in goles if g['equipo_id'] == partido['equipo_visitante_id'] and g['tipo'] == 'autogol')
    gv = sum(1 for g in goles if g['equipo_id'] == partido['equipo_visitante_id'] and g['tipo'] != 'autogol')
    gv += sum(1 for g in goles if g['equipo_id'] == partido['equipo_local_id'] and g['tipo'] == 'autogol')
    Partido.update_resultado(pid, gl, gv, partido['estado'])
    flash('Gol registrado', 'success')
    return redirect(url_for('partidos.detalle', pid=pid))


@partidos_bp.route('/<int:pid>/tarjeta', methods=['POST'])
@arbitro_required
def agregar_tarjeta(pid):
    Partido.registrar_tarjeta(
        pid,
        request.form['jugador_id'],
        request.form['equipo_id'],
        request.form['tipo'],
        request.form.get('minuto', 0),
        request.form.get('motivo', '')
    )
    flash('Tarjeta registrada', 'success')
    return redirect(url_for('partidos.detalle', pid=pid))


@partidos_bp.route('/<int:pid>/estado', methods=['POST'])
@arbitro_required
def cambiar_estado(pid):
    estado = request.form.get('estado')
    from app.database import execute_db
    execute_db("UPDATE partidos SET estado=? WHERE id=?", [estado, pid])
    flash(f'Estado cambiado a: {estado}', 'success')
    return redirect(url_for('partidos.detalle', pid=pid))
