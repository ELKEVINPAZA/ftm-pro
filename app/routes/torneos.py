"""Torneos routes: CRUD + fixture generation."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required, admin_required
from app.models import Torneo, FixtureGenerator

torneos_bp = Blueprint('torneos', __name__)


@torneos_bp.route('/')
@login_required
def index():
    torneos = Torneo.get_all()
    return render_template('torneos/index.html', torneos=torneos)


@torneos_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form['fecha_fin'],
            'max_equipos': int(request.form.get('max_equipos', 16)),
            'pts_victoria': int(request.form.get('pts_victoria', 3)),
            'pts_empate': int(request.form.get('pts_empate', 1)),
            'pts_derrota': int(request.form.get('pts_derrota', 0)),
            'reglas': request.form.get('reglas', ''),
        }
        tid = Torneo.create(data)
        flash('Torneo creado exitosamente', 'success')
        return redirect(url_for('torneos.detalle', tid=tid))
    return render_template('torneos/form.html', torneo=None)


@torneos_bp.route('/<int:tid>')
@login_required
def detalle(tid):
    torneo = Torneo.get_by_id(tid)
    if not torneo:
        flash('Torneo no encontrado', 'danger')
        return redirect(url_for('torneos.index'))
    stats = Torneo.get_stats(tid)
    return render_template('torneos/detalle.html', torneo=torneo, stats=stats)


@torneos_bp.route('/<int:tid>/activar')
@admin_required
def activar(tid):
    Torneo.update_estado(tid, 'activo')
    flash('Torneo activado', 'success')
    return redirect(url_for('torneos.detalle', tid=tid))


@torneos_bp.route('/<int:tid>/finalizar')
@admin_required
def finalizar(tid):
    Torneo.update_estado(tid, 'finalizado')
    flash('Torneo finalizado', 'info')
    return redirect(url_for('torneos.detalle', tid=tid))


@torneos_bp.route('/<int:tid>/fixture', methods=['POST'])
@admin_required
def generar_fixture(tid):
    torneo = Torneo.get_by_id(tid)
    fecha = request.form.get('fecha_inicio', torneo['fecha_inicio'] or '')
    
    if torneo['tipo'] == 'liga':
        ok, msg = FixtureGenerator.generar_liga(tid, fecha)
    else:
        ok, msg = FixtureGenerator.generar_eliminacion(tid, fecha)
    
    if ok:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('torneos.detalle', tid=tid))
