from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Usuario
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Solo administradores."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('rol') != 'admin':
            flash('Acceso restringido. Solo administradores.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


def arbitro_required(f):
    """Árbitros y administradores."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('rol') not in ('admin', 'arbitro'):
            flash('Acceso restringido.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = Usuario.verify_password(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            session['nombre'] = user['nombre_completo']
            flash(f'Bienvenido, {user["nombre_completo"] or user["username"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.login'))