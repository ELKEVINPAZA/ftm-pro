"""Jugadores routes."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.routes.auth import login_required, admin_required
from app.models import Jugador, Equipo

jugadores_bp = Blueprint('jugadores', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@jugadores_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    equipo_id = request.args.get('equipo_id', type=int)
    equipos = Equipo.get_all()
    if request.method == 'POST':
        foto_path = ''
        file = request.files.get('foto')
        if file and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'fotos')
            file.save(os.path.join(upload_dir, fname))
            foto_path = f'uploads/fotos/{fname}'
        
        data = {
            'equipo_id': request.form['equipo_id'],
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'numero_camiseta': request.form.get('numero_camiseta') or None,
            'posicion': request.form.get('posicion', ''),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
            'foto': foto_path,
        }
        jid = Jugador.create(data)
        flash('Jugador registrado', 'success')
        return redirect(url_for('equipos.detalle', eid=data['equipo_id']))
    return render_template('jugadores/form.html', jugador=None,
                           equipos=equipos, equipo_id=equipo_id)


@jugadores_bp.route('/<int:jid>/editar', methods=['GET', 'POST'])
@admin_required
def editar(jid):
    jugador = Jugador.get_by_id(jid)
    equipos = Equipo.get_all()
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'numero_camiseta': request.form.get('numero_camiseta') or None,
            'posicion': request.form.get('posicion', ''),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
        }
        Jugador.update(jid, data)
        flash('Jugador actualizado', 'success')
        return redirect(url_for('equipos.detalle', eid=jugador['equipo_id']))
    return render_template('jugadores/form.html', jugador=jugador,
                           equipos=equipos, equipo_id=jugador['equipo_id'])


@jugadores_bp.route('/<int:jid>/eliminar', methods=['POST'])
@admin_required
def eliminar(jid):
    jugador = Jugador.get_by_id(jid)
    Jugador.delete(jid)
    flash('Jugador eliminado', 'info')
    return redirect(url_for('equipos.detalle', eid=jugador['equipo_id']))
