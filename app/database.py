"""
Database connection and initialization module.
Uses SQLite with row_factory for dict-like access.
"""
import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash


def get_db():
    """Get database connection from Flask's g object."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute INSERT/UPDATE/DELETE query."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def init_db(app):
    """Initialize the database with schema."""
    db_path = app.config['DATABASE']
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'schema.sql')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Create tables from schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Strip comment lines, split on semicolons
    lines = [l for l in schema.splitlines() if not l.strip().startswith('--')]
    clean = '\n'.join(lines)
    statements = [s.strip() for s in clean.split(';') if s.strip()]
    creates = [s for s in statements if s.upper().lstrip().startswith('CREATE')]
    others  = [s for s in statements if not s.upper().lstrip().startswith('CREATE')]
    for s in creates:
        try:
            conn.execute(s)
        except Exception:
            pass
    conn.commit()
    for s in others:
        try:
            conn.execute(s)
        except Exception:
            pass
    
    # Create real admin user
    admin_exists = conn.execute("SELECT id FROM usuarios WHERE username='admin'").fetchone()
    if not admin_exists:
        conn.execute(
            "INSERT INTO usuarios (username, password_hash, rol, nombre_completo, email) VALUES (?,?,?,?,?)",
            ('admin', generate_password_hash('admin123'), 'admin', 'Administrador', 'admin@torneo.com')
        )
    else:
        # Update password hash to real one
        conn.execute(
            "UPDATE usuarios SET password_hash=? WHERE username='admin'",
            (generate_password_hash('admin123'),)
        )
    
    conn.commit()
    conn.close()
    
    app.teardown_appcontext(close_db)
