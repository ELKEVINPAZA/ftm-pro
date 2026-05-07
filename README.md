# ⚽ FTM Pro — Football Tournament Manager

Sistema completo de gestión de torneos de fútbol 11. Arquitectura web con Flask + SQLite.

---

## 🚀 Instalación rápida

```bash
# 1. Clonar / descomprimir el proyecto
cd football_manager

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python run.py
```

Abre el navegador en **http://localhost:5000**

- **Usuario:** `admin`  
- **Contraseña:** `admin123`

---

## 🧪 Cargar datos de demo

```bash
python seed_demo.py
```

Crea un torneo de prueba con 4 equipos, 44 jugadores, 2 jornadas y resultados de ejemplo.

---

## 📁 Estructura del proyecto

```
football_manager/
├── run.py                  # Punto de entrada
├── requirements.txt
├── seed_demo.py            # Datos de prueba
├── football.db             # Base de datos SQLite (se crea al iniciar)
├── scripts/
│   └── schema.sql          # Esquema de base de datos
└── app/
    ├── __init__.py
    ├── database.py         # Conexión y helpers SQLite
    ├── models.py           # Lógica de negocio (Torneo, Equipo, Jugador, etc.)
    ├── routes/
    │   ├── __init__.py     # Registro de blueprints
    │   ├── auth.py         # Login / logout
    │   ├── dashboard.py    # Panel principal
    │   ├── torneos.py      # CRUD torneos + fixture
    │   ├── equipos.py      # CRUD equipos
    │   ├── jugadores.py    # CRUD jugadores
    │   ├── partidos.py     # Partidos, goles, tarjetas
    │   ├── estadisticas.py # Tabla de posiciones, goleadores
    │   └── arbitros.py     # CRUD árbitros
    ├── templates/
    │   ├── base.html       # Layout con sidebar oscuro
    │   ├── auth/login.html
    │   ├── dashboard/index.html
    │   ├── torneos/
    │   ├── equipos/
    │   ├── jugadores/
    │   ├── partidos/
    │   ├── estadisticas/
    │   └── arbitros/
    └── static/
        └── uploads/
            ├── escudos/    # Logos de equipos
            └── fotos/      # Fotos de jugadores
```

---

## ✨ Funcionalidades

| Módulo | Función |
|--------|---------|
| 🏆 Torneos | Crear, activar, finalizar torneos. Liga o eliminación. |
| 🛡️ Equipos | Registro con escudo, entrenador, ciudad, contacto. |
| 👤 Jugadores | Plantilla completa por equipo, posición, foto. |
| ⚽ Partidos | Resultado, goles por jugador, tarjetas, estado en vivo. |
| 📊 Estadísticas | Tabla de posiciones, goleadores, fair play. |
| 🟨 Árbitros | Registro con licencia y contacto. |
| 📅 Fixture | Generación automática round-robin o eliminación. |

---

## 🗄️ Base de datos

Tablas principales:
- `usuarios` · `torneos` · `equipos` · `jugadores`
- `partidos` · `jornadas` · `goles` · `tarjetas`
- `sustituciones` · `arbitros` · `tabla_posiciones`

---

## 🔐 Roles

| Rol | Acceso |
|-----|--------|
| admin | Acceso total |
| arbitro | Gestión de partidos |
| delegado | Consulta |

---

## 📦 Dependencias

```
flask>=3.0.0
werkzeug>=3.0.0
```
Solo dos dependencias. Sin instalaciones complejas.

---

## 📸 Diseño

- Interfaz oscura tipo dashboard profesional
- Tipografía Syne (display) + DM Sans (body)
- Paleta verde esmeralda (#00e676) + teal (#1de9b6)
- Cards, badges, tablas dinámicas, sidebar fijo
- Responsive para móvil

---

**FTM Pro** · Desarrollado con Python + Flask + SQLite  
Listo para torneos amateur y semiprofesionales.
