"""Equipos routes."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.routes.auth import login_required, admin_required
from app.models import Equipo, Jugador, Torneo

equipos_bp = Blueprint('equipos', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@equipos_bp.route('/')
@login_required
def index():
    torneo_id = request.args.get('torneo_id', type=int)
    equipos = Equipo.get_all(torneo_id)
    torneos = Torneo.get_all()
    return render_template('equipos/index.html', equipos=equipos,
                           torneos=torneos, torneo_id=torneo_id)


@equipos_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    torneos = Torneo.get_all()
    if request.method == 'POST':
        escudo_path = ''
        file = request.files.get('escudo')
        if file and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'escudos')
            file.save(os.path.join(upload_dir, fname))
            escudo_path = f'uploads/escudos/{fname}'
        
        data = {
            'torneo_id': request.form.get('torneo_id'),
            'nombre': request.form['nombre'],
            'entrenador': request.form.get('entrenador', ''),
            'ciudad': request.form.get('ciudad', ''),
            'contacto': request.form.get('contacto', ''),
            'escudo': escudo_path,
            'min_jugadores': int(request.form.get('min_jugadores', 11)),
            'max_jugadores': int(request.form.get('max_jugadores', 25)),
        }
        eid = Equipo.create(data)
        flash('Equipo registrado', 'success')
        return redirect(url_for('equipos.detalle', eid=eid))
    return render_template('equipos/form.html', equipo=None, torneos=torneos)


@equipos_bp.route('/<int:eid>')
@login_required
def detalle(eid):
    equipo = Equipo.get_by_id(eid)
    if not equipo:
        flash('Equipo no encontrado', 'danger')
        return redirect(url_for('equipos.index'))
    jugadores = Jugador.get_by_equipo(eid)
    torneo = Torneo.get_by_id(equipo['torneo_id']) if equipo['torneo_id'] else None
    return render_template('equipos/detalle.html', equipo=equipo,
                           jugadores=jugadores, torneo=torneo)


@equipos_bp.route('/<int:eid>/editar', methods=['GET', 'POST'])
@admin_required
def editar(eid):
    equipo = Equipo.get_by_id(eid)
    torneos = Torneo.get_all()
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'entrenador': request.form.get('entrenador', ''),
            'ciudad': request.form.get('ciudad', ''),
            'contacto': request.form.get('contacto', ''),
            'min_jugadores': int(request.form.get('min_jugadores', 11)),
            'max_jugadores': int(request.form.get('max_jugadores', 25)),
        }
        Equipo.update(eid, data)
        flash('Equipo actualizado', 'success')
        return redirect(url_for('equipos.detalle', eid=eid))
    return render_template('equipos/form.html', equipo=equipo, torneos=torneos)


@equipos_bp.route('/<int:eid>/eliminar', methods=['POST'])
@admin_required
def eliminar(eid):
    Equipo.delete(eid)
    flash('Equipo eliminado', 'info')
    return redirect(url_for('equipos.index'))
