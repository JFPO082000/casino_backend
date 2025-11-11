from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import db_connect
import psycopg2
from psycopg2.extras import RealDictCursor
import decimal # Importamos decimal para manejar dinero
from datetime import datetime # Para manejar fechas

router = APIRouter()

# ==========================================================
#  ESTADÍSTICAS Y LISTAS (Ya existentes)
# ==========================================================
@router.get("/api/admin/stats")
async def api_get_admin_stats():
[Immersive content redacted for brevity.]
@router.get("/api/admin/administradores")
async def api_get_all_admins():
[Immersive content redacted for brevity.]
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
#  NUEVO: GESTIÓN DE PROMOCIONES (Para 'admin-promociones.html')
# ==========================================================

@router.get("/api/admin/bonos")
async def api_get_all_bonos():
    """
    Obtiene la lista de todos los Bonos (promociones)
    para el panel de admin.
    """
    print(f"🔹 API Admin: Pidiendo lista de bonos")
    conn = None
    try:
        conn = db_connect.get_connection()
        if conn is None: return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Bono ORDER BY nombre_bono")
        bonos = cursor.fetchall()
        cursor.close()
        
        return JSONResponse({"bonos": bonos})

    except Exception as e:
        print(f"🚨 API ERROR (Admin Get Bonos): {e}")
        return JSONResponse({"error": f"Error interno: {e}"}, status_code=500)
    finally:
        if conn: conn.close()

@router.post("/api/admin/bonos")
async def api_create_bono(
    nombre_bono: str = Form(),
    tipo: str = Form(),
    descripcion: str = Form(),
    fecha_expiracion: str = Form(), # Llega como "YYYY-MM-DD"
    activo: str = Form() # "true" o "false"
):
    """
    Crea un nuevo Bono maestro en la tabla 'Bono'.
    """
    print(f"🔹 API Admin: Creando nuevo bono: {nombre_bono}")
    conn = None
    cursor = None
    try:
        # 1. Validar y convertir tipos
        try:
            # Convertir la fecha. Si viene vacía, la guardamos como NULL
            fecha_exp = None
            if fecha_expiracion:
                fecha_exp = datetime.strptime(fecha_expiracion, '%Y-%m-%d').date()
            
            activo_bool = (activo.lower() == 'true')
        except Exception:
            return JSONResponse({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}, status_code=400)
        
        # 2. Conectar e insertar
        conn = db_connect.get_connection()
        if conn is None: return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Bono (nombre_bono, tipo, descripcion, fecha_expiracion, activo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nombre_bono, tipo, descripcion, fecha_exp, activo_bool)
        )
        conn.commit()
        
        print(f"✅ API Admin: Bono '{nombre_bono}' creado.")
        return JSONResponse({"success": True, "message": "Promoción creada con éxito."})

    except psycopg2.errors.UniqueViolation:
        if conn: conn.rollback()
        return JSONResponse({"error": "El nombre de esa promoción ya existe."}, status_code=409)
    except Exception as e:
        if conn: conn.rollback()
        print(f"🚨 API ERROR (Admin Create Bono): {e}")
        return JSONResponse({"error": f"Error interno: {e}"}, status_code=500)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
