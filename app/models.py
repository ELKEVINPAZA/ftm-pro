"""
Models - Business logic layer for all entities.
Each model class handles CRUD and business rules.
"""
from app.database import query_db, execute_db, get_db
from werkzeug.security import generate_password_hash, check_password_hash
import itertools
import random
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────
class Usuario:
    @staticmethod
    def get_by_username(username):
        return query_db("SELECT * FROM usuarios WHERE username=?", [username], one=True)

    @staticmethod
    def get_by_id(uid):
        return query_db("SELECT * FROM usuarios WHERE id=?", [uid], one=True)

    @staticmethod
    def verify_password(username, password):
        user = Usuario.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    @staticmethod
    def create(username, password, rol, nombre_completo='', email=''):
        h = generate_password_hash(password)
        return execute_db(
            "INSERT INTO usuarios (username,password_hash,rol,nombre_completo,email) VALUES (?,?,?,?,?)",
            [username, h, rol, nombre_completo, email]
        )

    @staticmethod
    def get_all():
        return query_db("SELECT * FROM usuarios ORDER BY nombre_completo")


# ─────────────────────────────────────────────
# TORNEO MODEL
# ─────────────────────────────────────────────
class Torneo:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM torneos ORDER BY creado_en DESC")

    @staticmethod
    def get_by_id(tid):
        return query_db("SELECT * FROM torneos WHERE id=?", [tid], one=True)

    @staticmethod
    def get_activo():
        return query_db("SELECT * FROM torneos WHERE estado='activo' LIMIT 1", one=True)

    @staticmethod
    def create(data):
        return execute_db(
            """INSERT INTO torneos (nombre,tipo,fecha_inicio,fecha_fin,max_equipos,
               pts_victoria,pts_empate,pts_derrota,reglas,estado)
               VALUES (?,?,?,?,?,?,?,?,?,'pendiente')""",
            [data['nombre'], data['tipo'], data['fecha_inicio'], data['fecha_fin'],
             data['max_equipos'], data['pts_victoria'], data['pts_empate'],
             data['pts_derrota'], data.get('reglas','')]
        )

    @staticmethod
    def update_estado(tid, estado):
        execute_db("UPDATE torneos SET estado=? WHERE id=?", [estado, tid])

    @staticmethod
    def get_stats(tid):
        equipos = query_db("SELECT COUNT(*) as c FROM equipos WHERE torneo_id=?", [tid], one=True)
        partidos = query_db("SELECT COUNT(*) as c FROM partidos WHERE torneo_id=?", [tid], one=True)
        finalizados = query_db(
            "SELECT COUNT(*) as c FROM partidos WHERE torneo_id=? AND estado='finalizado'", [tid], one=True
        )
        return {
            'equipos': equipos['c'] if equipos else 0,
            'partidos': partidos['c'] if partidos else 0,
            'finalizados': finalizados['c'] if finalizados else 0,
        }


# ─────────────────────────────────────────────
# EQUIPO MODEL
# ─────────────────────────────────────────────
class Equipo:
    @staticmethod
    def get_all(torneo_id=None):
        if torneo_id:
            return query_db("SELECT * FROM equipos WHERE torneo_id=? AND activo=1 ORDER BY nombre", [torneo_id])
        return query_db("SELECT * FROM equipos WHERE activo=1 ORDER BY nombre")

    @staticmethod
    def get_by_id(eid):
        return query_db("SELECT * FROM equipos WHERE id=?", [eid], one=True)

    @staticmethod
    def create(data):
        return execute_db(
            """INSERT INTO equipos (torneo_id,nombre,entrenador,ciudad,contacto,escudo,
               min_jugadores,max_jugadores) VALUES (?,?,?,?,?,?,?,?)""",
            [data['torneo_id'], data['nombre'], data.get('entrenador',''),
             data.get('ciudad',''), data.get('contacto',''), data.get('escudo',''),
             data.get('min_jugadores',11), data.get('max_jugadores',25)]
        )

    @staticmethod
    def update(eid, data):
        execute_db(
            """UPDATE equipos SET nombre=?,entrenador=?,ciudad=?,contacto=?,
               min_jugadores=?,max_jugadores=? WHERE id=?""",
            [data['nombre'], data.get('entrenador',''), data.get('ciudad',''),
             data.get('contacto',''), data.get('min_jugadores',11),
             data.get('max_jugadores',25), eid]
        )

    @staticmethod
    def delete(eid):
        execute_db("UPDATE equipos SET activo=0 WHERE id=?", [eid])

    @staticmethod
    def count_jugadores(eid):
        r = query_db("SELECT COUNT(*) as c FROM jugadores WHERE equipo_id=? AND activo=1", [eid], one=True)
        return r['c'] if r else 0


# ─────────────────────────────────────────────
# JUGADOR MODEL
# ─────────────────────────────────────────────
class Jugador:
    @staticmethod
    def get_by_equipo(equipo_id):
        return query_db(
            "SELECT * FROM jugadores WHERE equipo_id=? AND activo=1 ORDER BY numero_camiseta",
            [equipo_id]
        )

    @staticmethod
    def get_by_id(jid):
        return query_db("SELECT * FROM jugadores WHERE id=?", [jid], one=True)

    @staticmethod
    def create(data):
        return execute_db(
            """INSERT INTO jugadores (equipo_id,nombre,apellido,numero_camiseta,
               posicion,fecha_nacimiento,foto) VALUES (?,?,?,?,?,?,?)""",
            [data['equipo_id'], data['nombre'], data['apellido'],
             data.get('numero_camiseta'), data.get('posicion',''),
             data.get('fecha_nacimiento',''), data.get('foto','')]
        )

    @staticmethod
    def update(jid, data):
        execute_db(
            """UPDATE jugadores SET nombre=?,apellido=?,numero_camiseta=?,
               posicion=?,fecha_nacimiento=? WHERE id=?""",
            [data['nombre'], data['apellido'], data.get('numero_camiseta'),
             data.get('posicion',''), data.get('fecha_nacimiento',''), jid]
        )

    @staticmethod
    def delete(jid):
        execute_db("UPDATE jugadores SET activo=0 WHERE id=?", [jid])

    @staticmethod
    def get_stats(jid, torneo_id=None):
        q_goles = """SELECT COUNT(*) as c FROM goles g
                     JOIN partidos p ON g.partido_id=p.id
                     WHERE g.jugador_id=? AND g.tipo!='autogol'"""
        q_amarillas = """SELECT COUNT(*) as c FROM tarjetas t
                         JOIN partidos p ON t.partido_id=p.id
                         WHERE t.jugador_id=? AND t.tipo='amarilla'"""
        q_rojas = """SELECT COUNT(*) as c FROM tarjetas t
                     JOIN partidos p ON t.partido_id=p.id
                     WHERE t.jugador_id=? AND t.tipo IN ('roja','doble_amarilla')"""
        args = [jid]
        if torneo_id:
            q_goles += " AND p.torneo_id=?"
            q_amarillas += " AND p.torneo_id=?"
            q_rojas += " AND p.torneo_id=?"
            args = [jid, torneo_id]
        goles = query_db(q_goles, args, one=True)
        amarillas = query_db(q_amarillas, args, one=True)
        rojas = query_db(q_rojas, args, one=True)
        return {
            'goles': goles['c'] if goles else 0,
            'amarillas': amarillas['c'] if amarillas else 0,
            'rojas': rojas['c'] if rojas else 0,
        }


# ─────────────────────────────────────────────
# PARTIDO MODEL
# ─────────────────────────────────────────────
class Partido:
    @staticmethod
    def get_all(torneo_id=None, estado=None):
        q = """SELECT p.*, 
               el.nombre as local_nombre, el.escudo as local_escudo,
               ev.nombre as visitante_nombre, ev.escudo as visitante_escudo,
               a.nombre || ' ' || a.apellido as arbitro_nombre,
               j.numero as jornada_num
               FROM partidos p
               LEFT JOIN equipos el ON p.equipo_local_id=el.id
               LEFT JOIN equipos ev ON p.equipo_visitante_id=ev.id
               LEFT JOIN arbitros a ON p.arbitro_id=a.id
               LEFT JOIN jornadas j ON p.jornada_id=j.id
               WHERE 1=1"""
        args = []
        if torneo_id:
            q += " AND p.torneo_id=?"
            args.append(torneo_id)
        if estado:
            q += " AND p.estado=?"
            args.append(estado)
        q += " ORDER BY p.fecha ASC, p.id ASC"
        return query_db(q, args)

    @staticmethod
    def get_by_id(pid):
        return query_db(
            """SELECT p.*, 
               el.nombre as local_nombre, el.escudo as local_escudo,
               ev.nombre as visitante_nombre, ev.escudo as visitante_escudo,
               a.nombre || ' ' || a.apellido as arbitro_nombre
               FROM partidos p
               LEFT JOIN equipos el ON p.equipo_local_id=el.id
               LEFT JOIN equipos ev ON p.equipo_visitante_id=ev.id
               LEFT JOIN arbitros a ON p.arbitro_id=a.id
               WHERE p.id=?""", [pid], one=True
        )

    @staticmethod
    def create(data):
        return execute_db(
            """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,equipo_visitante_id,
               arbitro_id,fecha,cancha,estado,fase) VALUES (?,?,?,?,?,?,?,?,?)""",
            [data['torneo_id'], data.get('jornada_id'), data['equipo_local_id'],
             data['equipo_visitante_id'], data.get('arbitro_id'), data.get('fecha'),
             data.get('cancha',''), data.get('estado','pendiente'), data.get('fase','grupo')]
        )

    @staticmethod
    def update_resultado(pid, goles_local, goles_visitante, estado='finalizado'):
        execute_db(
            "UPDATE partidos SET goles_local=?,goles_visitante=?,estado=? WHERE id=?",
            [goles_local, goles_visitante, estado, pid]
        )

    @staticmethod
    def get_goles(pid):
        return query_db(
            """SELECT g.*, j.nombre || ' ' || j.apellido as jugador_nombre,
               j.numero_camiseta, e.nombre as equipo_nombre
               FROM goles g
               JOIN jugadores j ON g.jugador_id=j.id
               JOIN equipos e ON g.equipo_id=e.id
               WHERE g.partido_id=? ORDER BY g.minuto""", [pid]
        )

    @staticmethod
    def get_tarjetas(pid):
        return query_db(
            """SELECT t.*, j.nombre || ' ' || j.apellido as jugador_nombre,
               j.numero_camiseta, e.nombre as equipo_nombre
               FROM tarjetas t
               JOIN jugadores j ON t.jugador_id=j.id
               JOIN equipos e ON t.equipo_id=e.id
               WHERE t.partido_id=? ORDER BY t.minuto""", [pid]
        )

    @staticmethod
    def registrar_gol(partido_id, jugador_id, equipo_id, minuto, tipo='normal'):
        return execute_db(
            "INSERT INTO goles (partido_id,jugador_id,equipo_id,minuto,tipo) VALUES (?,?,?,?,?)",
            [partido_id, jugador_id, equipo_id, minuto, tipo]
        )

    @staticmethod
    def registrar_tarjeta(partido_id, jugador_id, equipo_id, tipo, minuto, motivo=''):
        return execute_db(
            "INSERT INTO tarjetas (partido_id,jugador_id,equipo_id,tipo,minuto,motivo) VALUES (?,?,?,?,?,?)",
            [partido_id, jugador_id, equipo_id, tipo, minuto, motivo]
        )


# ─────────────────────────────────────────────
# FIXTURE GENERATOR
# ─────────────────────────────────────────────
class FixtureGenerator:
    @staticmethod
    def generar_liga(torneo_id, fecha_inicio_str):
        """Round-robin fixture generator."""
        equipos = Equipo.get_all(torneo_id)
        if len(equipos) < 2:
            return False, "Se necesitan al menos 2 equipos"

        ids = [e['id'] for e in equipos]
        if len(ids) % 2 != 0:
            ids.append(None)  # bye

        n = len(ids)
        jornada_num = 0
        try:
            fecha_base = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        except Exception:
            fecha_base = datetime.now()

        for ronda in range(n - 1):
            jornada_num += 1
            fecha_jornada = fecha_base + timedelta(weeks=ronda)
            jid = execute_db(
                "INSERT INTO jornadas (torneo_id,numero,nombre,fecha) VALUES (?,?,?,?)",
                [torneo_id, jornada_num, f"Jornada {jornada_num}", fecha_jornada.strftime('%Y-%m-%d')]
            )
            for i in range(n // 2):
                local = ids[i]
                visitante = ids[n - 1 - i]
                if local is None or visitante is None:
                    continue
                hora = f"{fecha_jornada.strftime('%Y-%m-%d')} {10 + i * 2}:00"
                canchas = ['Cancha A', 'Cancha B', 'Cancha C']
                execute_db(
                    """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,
                       equipo_visitante_id,fecha,cancha,estado)
                       VALUES (?,?,?,?,?,?,?)""",
                    [torneo_id, jid, local, visitante, hora,
                     canchas[i % len(canchas)], 'pendiente']
                )
            # Rotate
            ids.insert(1, ids.pop())

        return True, f"Fixture generado: {jornada_num} jornadas"

    @staticmethod
    def generar_eliminacion(torneo_id, fecha_inicio_str):
        """Single elimination bracket."""
        equipos = list(Equipo.get_all(torneo_id))
        random.shuffle(equipos)
        try:
            fecha_base = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        except Exception:
            fecha_base = datetime.now()

        fases = ['Octavos','Cuartos','Semifinal','Final']
        ronda = 0
        jid = execute_db(
            "INSERT INTO jornadas (torneo_id,numero,nombre,fecha) VALUES (?,?,?,?)",
            [torneo_id, 1, fases[min(ronda, len(fases)-1)],
             fecha_base.strftime('%Y-%m-%d')]
        )
        for i in range(0, len(equipos) - 1, 2):
            if i + 1 < len(equipos):
                execute_db(
                    """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,
                       equipo_visitante_id,fecha,cancha,estado,fase)
                       VALUES (?,?,?,?,?,?,'pendiente',?)""",
                    [torneo_id, jid, equipos[i]['id'], equipos[i+1]['id'],
                     fecha_base.strftime('%Y-%m-%d %H:%M'), 'Cancha A', 'eliminacion']
                )
        return True, "Fase de eliminación generada"


# ─────────────────────────────────────────────
# STANDINGS / TABLA DE POSICIONES
# ─────────────────────────────────────────────
class TablaPosiciones:
    @staticmethod
    def calcular(torneo_id):
        torneo = Torneo.get_by_id(torneo_id)
        if not torneo:
            return []
        
        pts_v = torneo['pts_victoria']
        pts_e = torneo['pts_empate']
        pts_d = torneo['pts_derrota']

        equipos = Equipo.get_all(torneo_id)
        partidos = query_db(
            """SELECT * FROM partidos WHERE torneo_id=? AND estado='finalizado'""",
            [torneo_id]
        )

        stats = {}
        for e in equipos:
            stats[e['id']] = {
                'equipo_id': e['id'], 'nombre': e['nombre'], 'escudo': e['escudo'],
                'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0,
                'gf': 0, 'gc': 0, 'dg': 0, 'puntos': 0
            }

        for p in partidos:
            lid = p['equipo_local_id']
            vid = p['equipo_visitante_id']
            gl = p['goles_local']
            gv = p['goles_visitante']

            if lid in stats:
                stats[lid]['pj'] += 1
                stats[lid]['gf'] += gl
                stats[lid]['gc'] += gv
                if gl > gv:
                    stats[lid]['pg'] += 1
                    stats[lid]['puntos'] += pts_v
                elif gl == gv:
                    stats[lid]['pe'] += 1
                    stats[lid]['puntos'] += pts_e
                else:
                    stats[lid]['pp'] += 1
                    stats[lid]['puntos'] += pts_d

            if vid in stats:
                stats[vid]['pj'] += 1
                stats[vid]['gf'] += gv
                stats[vid]['gc'] += gl
                if gv > gl:
                    stats[vid]['pg'] += 1
                    stats[vid]['puntos'] += pts_v
                elif gv == gl:
                    stats[vid]['pe'] += 1
                    stats[vid]['puntos'] += pts_e
                else:
                    stats[vid]['pp'] += 1
                    stats[vid]['puntos'] += pts_d

        for s in stats.values():
            s['dg'] = s['gf'] - s['gc']

        tabla = sorted(stats.values(),
                       key=lambda x: (x['puntos'], x['dg'], x['gf']),
                       reverse=True)
        return tabla

    @staticmethod
    def goleadores(torneo_id, limit=10):
        return query_db(
            """SELECT j.nombre || ' ' || j.apellido as jugador,
               j.numero_camiseta, e.nombre as equipo, e.escudo,
               COUNT(g.id) as goles
               FROM goles g
               JOIN jugadores j ON g.jugador_id=j.id
               JOIN equipos e ON g.equipo_id=e.id
               JOIN partidos p ON g.partido_id=p.id
               WHERE p.torneo_id=? AND g.tipo!='autogol'
               GROUP BY g.jugador_id
               ORDER BY goles DESC LIMIT ?""",
            [torneo_id, limit]
        )

    @staticmethod
    def fair_play(torneo_id):
        return query_db(
            """SELECT e.nombre as equipo, e.escudo,
               SUM(CASE WHEN t.tipo='amarilla' THEN 1 ELSE 0 END) as amarillas,
               SUM(CASE WHEN t.tipo IN ('roja','doble_amarilla') THEN 1 ELSE 0 END) as rojas,
               SUM(CASE WHEN t.tipo='amarilla' THEN 1 ELSE 0 END) +
               SUM(CASE WHEN t.tipo IN ('roja','doble_amarilla') THEN 3 ELSE 0 END) as puntos_fp
               FROM tarjetas t
               JOIN equipos e ON t.equipo_id=e.id
               JOIN partidos p ON t.partido_id=p.id
               WHERE p.torneo_id=?
               GROUP BY t.equipo_id
               ORDER BY puntos_fp ASC""",
            [torneo_id]
        )


# ─────────────────────────────────────────────
# ARBITRO MODEL
# ─────────────────────────────────────────────
class Arbitro:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM arbitros WHERE activo=1 ORDER BY apellido")

    @staticmethod
    def get_by_id(aid):
        return query_db("SELECT * FROM arbitros WHERE id=?", [aid], one=True)

    @staticmethod
    def create(data):
        return execute_db(
            "INSERT INTO arbitros (nombre,apellido,licencia,telefono) VALUES (?,?,?,?)",
            [data['nombre'], data['apellido'], data.get('licencia',''), data.get('telefono','')]
        )
