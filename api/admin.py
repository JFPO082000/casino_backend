from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.db import db_connect # <-- CORRECCIÓN: Importación relativa
import psycopg2
from psycopg2.extras import RealDictCursor
import decimal # Importamos decimal para manejar dinero
from datetime import datetime # Para manejar fechas

router = APIRouter()

# ==========================================================
#  ESTADÍSTICAS (Ya existente)
# ==========================================================
@router.get("/api/admin/stats")
async def api_get_admin_stats():
    """
    Obtiene estadísticas clave para el dashboard del administrador.
    Llamada por: admin-info-general.html
    """
    print("🔹 API Admin: Pidiendo estadísticas generales")
    conn = None
    try:
        conn = db_connect.get_connection()
        if conn is None:
            return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Total de usuarios (solo jugadores)
        cursor.execute("SELECT COUNT(*) as total_users FROM Usuario WHERE rol = 'Jugador'")
        total_users = cursor.fetchone()['total_users']
        
        # 2. Total de juegos activos
        cursor.execute("SELECT COUNT(*) as active_games FROM Juego WHERE activo = true")
        active_games = cursor.fetchone()['active_games']
        
        # 3. Total de depósitos hoy
        cursor.execute(
            "SELECT COALESCE(SUM(monto), 0) as deposits_today FROM Transaccion WHERE tipo_transaccion = 'Depósito' AND estado = 'Completado' AND fecha_transaccion >= CURRENT_DATE"
        )
        deposits_today = cursor.fetchone()['deposits_today']
        
        cursor.close()
        
        return JSONResponse({
            "total_users": total_users,
            "active_games": active_games,
            "deposits_today": float(deposits_today)
        })

    except Exception as e:
        print(f"🚨 API ERROR (Admin Stats): {e}")
        return JSONResponse({"error": f"Error interno: {e}"}, status_code=500)
    finally:
        if conn: conn.close()

# ==========================================================
#  NUEVO: LISTAR USUARIOS Y ADMINS
# ==========================================================
@router.get("/api/admin/usuarios")
async def api_get_all_users():
    """
    Obtiene la lista de todos los usuarios con rol 'Jugador'.
    Llamada por: admin-usuarios.html
    """
    print(f"🔹 API Admin: Pidiendo lista de Jugadores")
    conn = None
    try:
        conn = db_connect.get_connection()
        if conn is None: return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscamos solo Jugadores
        cursor.execute(
            "SELECT id_usuario, nombre, apellido, email, activo FROM Usuario WHERE rol = 'Jugador' ORDER BY nombre",
        )
        usuarios = cursor.fetchall()
        cursor.close()
        
        return JSONResponse({"users": usuarios})

    except Exception as e:
        print(f"🚨 API ERROR (Admin Get Jugadores): {e}")
        return JSONResponse({"error": f"Error interno: {e}"}, status_code=500)
    finally:
        if conn: conn.close()

@router.get("/api/admin/administradores")
async def api_get_all_admins():
    """
    Obtiene la lista de todos los usuarios con rol 'Administrador' o 'Auditor'.
    Llamada por: admin-administradores.html
    """
    print(f"🔹 API Admin: Pidiendo lista de Admins/Auditores")
    conn = None
    try:
        conn = db_connect.get_connection()
        if conn is None: return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscamos Admins y Auditores
        cursor.execute(
            "SELECT id_usuario, nombre, apellido, email, rol, activo FROM Usuario WHERE rol IN ('Administrador', 'Auditor') ORDER BY nombre",
        )
        admins = cursor.fetchall()
        cursor.close()
        
        return JSONResponse({"admins": admins})

    except Exception as e:
        print(f"🚨 API ERROR (Admin Get Admins): {e}")
        return JSONResponse({"error": f"Error interno: {e}"}, status_code=500)
    finally:
        if conn: conn.close()

# ==========================================================
#  GESTIÓN DE PERFIL DE USUARIO (Ya existente)
# ==========================================================
@router.get("/api/admin/user-profile/{id_usuario}")
async def api_get_user_profile(id_usuario: int):
[Immersive content redacted for brevity.]
@router.put("/api/admin/user-profile/{id_usuario}")
async def api_update_user_profile(
    id_usuario: int,
[Immersive content redacted for brevity.]
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ==========================================================
#  GESTIÓN DE JUEGOS (Ya existente)
# ==========================================================
@router.get("/api/admin/games")
async def api_get_all_games():
[Immersive content redacted for brevity.]
@router.post("/api/admin/games")
async def api_create_game(
    nombre: str = Form(),
[Immersive content redacted for brevity.]
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ==========================================================
#  GESTIÓN DE PROMOCIONES (Ya existente)
# ==========================================================
@router.get("/api/admin/bonos")
async def api_get_all_bonos():
[Immersive content redacted for brevity.]
@router.post("/api/admin/bonos")
async def api_create_bono(
    nombre_bono: str = Form(),
[Immersive content redacted for brevity.]
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
