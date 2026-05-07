"""
seed_demo.py — Carga datos de demostración para probar el sistema.
Ejecutar: python seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import create_app
from app.database import get_db, execute_db
from app.models import Torneo, Equipo, Jugador, Partido, Arbitro

app = create_app()

EQUIPOS = [
    ("Atlético Ciudad",   "Carlos Ramírez",  "Norte"),
    ("Deportivo FC",      "Jhon Pérez",      "Sur"),
    ("Real United",       "Miguel Torres",   "Centro"),
    ("Club Olímpico",     "Andrés Silva",    "Oriente"),
]

JUGADORES = [
    ("Carlos","Gómez","Portero",1),
    ("Luis","Martínez","Defensa",4),
    ("Jhon","Torres","Defensa",5),
    ("Miguel","Pérez","Defensa",6),
    ("Andrés","López","Mediocampista",8),
    ("Diego","Castro","Mediocampista",10),
    ("Felipe","Ríos","Mediocampista",7),
    ("Sebastián","Mora","Delantero",9),
    ("Camilo","Vargas","Delantero",11),
    ("Nicolás","Soto","Defensa",3),
    ("Esteban","Ruiz","Mediocampista",12),
]

with app.app_context():
    db = get_db()

    # Torneo
    tid = execute_db(
        """INSERT INTO torneos (nombre,tipo,fecha_inicio,fecha_fin,max_equipos,
           pts_victoria,pts_empate,pts_derrota,estado,reglas)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        ["Copa Demo 2024","liga","2024-03-01","2024-06-30",
         8,3,1,0,"activo",
         "Torneo de liga todos contra todos. Clasifican los 2 primeros."]
    )
    print(f"✅ Torneo creado (id={tid})")

    # Árbitro
    aid = execute_db(
        "INSERT INTO arbitros (nombre,apellido,licencia,telefono) VALUES (?,?,?,?)",
        ["Jorge","Hernández","ARB-001","300-123-4567"]
    )

    # Equipos + Jugadores
    eids = []
    for nombre, dt, ciudad in EQUIPOS:
        eid = execute_db(
            """INSERT INTO equipos (torneo_id,nombre,entrenador,ciudad,
               min_jugadores,max_jugadores) VALUES (?,?,?,?,?,?)""",
            [tid, nombre, dt, ciudad, 11, 25]
        )
        eids.append(eid)
        print(f"  🛡️  {nombre} (id={eid})")
        for j in JUGADORES:
            execute_db(
                """INSERT INTO jugadores (equipo_id,nombre,apellido,posicion,
                   numero_camiseta,fecha_nacimiento) VALUES (?,?,?,?,?,?)""",
                [eid, j[0], j[1], j[2], j[3], "1998-05-15"]
            )

    # Partidos (jornada 1 ya jugada)
    from app.database import execute_db as ex
    jid = execute_db(
        "INSERT INTO jornadas (torneo_id,numero,nombre,fecha) VALUES (?,?,?,?)",
        [tid,1,"Jornada 1","2024-03-08"]
    )
    # Match 1: Atletico 3-1 Deportivo
    p1 = execute_db(
        """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,equipo_visitante_id,
           arbitro_id,fecha,cancha,goles_local,goles_visitante,estado)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [tid,jid,eids[0],eids[1],aid,"2024-03-08 10:00","Cancha A",3,1,"finalizado"]
    )
    # Match 2: Real United 2-2 Olímpico
    p2 = execute_db(
        """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,equipo_visitante_id,
           arbitro_id,fecha,cancha,goles_local,goles_visitante,estado)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [tid,jid,eids[2],eids[3],aid,"2024-03-08 12:00","Cancha B",2,2,"finalizado"]
    )
    # Goles partido 1
    jugAtl = db.execute(
        "SELECT id FROM jugadores WHERE equipo_id=? ORDER BY numero_camiseta LIMIT 11", [eids[0]]
    ).fetchall()
    jugDep = db.execute(
        "SELECT id FROM jugadores WHERE equipo_id=? ORDER BY numero_camiseta LIMIT 11", [eids[1]]
    ).fetchall()
    for jug, min_ in [(jugAtl[7]['id'],12),(jugAtl[8]['id'],34),(jugAtl[5]['id'],67)]:
        execute_db(
            "INSERT INTO goles (partido_id,jugador_id,equipo_id,minuto,tipo) VALUES (?,?,?,?,?)",
            [p1, jug, eids[0], min_, "normal"]
        )
    execute_db(
        "INSERT INTO goles (partido_id,jugador_id,equipo_id,minuto,tipo) VALUES (?,?,?,?,?)",
        [p1, jugDep[8]['id'], eids[1], 55, "normal"]
    )
    # Tarjeta
    execute_db(
        "INSERT INTO tarjetas (partido_id,jugador_id,equipo_id,tipo,minuto) VALUES (?,?,?,?,?)",
        [p1, jugDep[3]['id'], eids[1], "amarilla", 40]
    )

    # Jornada 2 pendiente
    jid2 = execute_db(
        "INSERT INTO jornadas (torneo_id,numero,nombre,fecha) VALUES (?,?,?,?)",
        [tid,2,"Jornada 2","2024-03-15"]
    )
    execute_db(
        """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,equipo_visitante_id,
           fecha,cancha,estado) VALUES (?,?,?,?,?,?,?)""",
        [tid,jid2,eids[1],eids[2],"2024-03-15 10:00","Cancha A","pendiente"]
    )
    execute_db(
        """INSERT INTO partidos (torneo_id,jornada_id,equipo_local_id,equipo_visitante_id,
           fecha,cancha,estado) VALUES (?,?,?,?,?,?,?)""",
        [tid,jid2,eids[3],eids[0],"2024-03-15 12:00","Cancha B","pendiente"]
    )

    db.commit()
    print("\n✅ Datos de demo cargados exitosamente.")
    print("   Abre http://localhost:5000 y usa admin / admin123")
