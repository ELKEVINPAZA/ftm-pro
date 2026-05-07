from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required, admin_required
from app.models import Usuario

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/') 
@admin_required
def index():
    usuarios = Usuario.get_all()
    return render_template('usuarios/index.html', usuarios=usuarios)

@usuarios_bp.route('/nuevo', methods=['GET','POST'])
@admin_required
def nuevo():
    if request.method == 'POST':
        try:
            Usuario.create(
                request.form['username'],
                request.form['password'],
                request.form['rol'],
                request.form.get('nombre_completo',''),
                request.form.get('email','')
            )
            flash('Usuario creado', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception:
            flash('El usuario ya existe', 'danger')
    return render_template('usuarios/form.html')

@usuarios_bp.route('/<int:uid>/eliminar', methods=['POST'])
@admin_required
def eliminar(uid):
    if uid == 1:
        flash('No puedes eliminar el admin principal', 'danger')
    else:
        from app.database import execute_db
        execute_db("UPDATE usuarios SET activo=0 WHERE id=?", [uid])
        flash('Usuario desactivado', 'info')
    return redirect(url_for('usuarios.index'))