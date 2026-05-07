"""Arbitros routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models import Arbitro

arbitros_bp = Blueprint('arbitros', __name__)


@arbitros_bp.route('/')
@login_required
def index():
    arbitros = Arbitro.get_all()
    return render_template('arbitros/index.html', arbitros=arbitros)


@arbitros_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'licencia': request.form.get('licencia', ''),
            'telefono': request.form.get('telefono', ''),
        }
        Arbitro.create(data)
        flash('Árbitro registrado', 'success')
        return redirect(url_for('arbitros.index'))
    return render_template('arbitros/form.html')
