from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import db_connect  # Tu archivo db_connect.py
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext  # Para verificar contraseñas

# Configura el contexto de hasheo (debe coincidir con cómo guardaste la contraseña)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Creamos un "router". Es como una mini-app de FastAPI
router = APIRouter()

@router.post("/api/auth/login")
async def api_login(correo: str = Form(), contrasena: str = Form()):
    """
    Esta es la ruta de API que tu login.html llama.
    USA LOS NOMBRES DE TU ESQUEMA SQL.
    """
    print(f"🔹 API: Intento de login para: {correo}")
    conn = None
    try:
        # 1. Obtenemos conexión de db_connect.py
        conn = db_connect.get_connection()
        if conn is None:
            return JSONResponse({"error": "Error de conexión con la base de datos"}, status_code=500)
        
        # 2. Creamos un cursor que devuelve diccionarios (más fácil)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 3. Buscamos al usuario SOLO POR EMAIL
        # Usamos los nombres de tu tabla: usuarios, email
        cursor.execute(
            "SELECT id_usuario, rol, contrasena_hash FROM usuarios WHERE email = %s", 
            (correo,)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            # Si el email no existe, cerramos todo y damos error
            print("❌ API: Email no encontrado")
            cursor.close()
            conn.close()
            return JSONResponse({"error": "Correo o contraseña incorrectos"}, status_code=401)

        # 4. Verificamos la contraseña
        # Compara la 'contrasena' (texto plano) del formulario
        # con la 'contrasena_hash' (hash) de la base de datos
        if not pwd_context.verify(contrasena, usuario["contrasena_hash"]):
            print("❌ API: Contraseña incorrecta")
            cursor.close()
            conn.close()
            return JSONResponse({"error": "Correo o contraseña incorrectos"}, status_code=401)
        
        # 5. ¡Éxito! Cerramos y devolvemos el JSON
        cursor.close()
        
        print(f"✅ API: Login exitoso para {usuario['id_usuario']}")
        # Devolvemos el JSON que tu login.html espera
        return JSONResponse({
            "id_usuario": usuario['id_usuario'],
            "rol": usuario['rol']
        })

    except Exception as e:
        print(f"🚨 API ERROR (Login): {e}")
        return JSONResponse({"error": f"Error interno del servidor: {e}"}, status_code=500)
    finally:
        if conn:
            conn.close()


# ==========================================================
#  NUEVA RUTA PARA REGISTRO
# ==========================================================
@router.post("/api/auth/register")
async def api_register(
    correo: str = Form(),
    curp: str = Form(),
    nombre: str = Form(),
    apellido: str = Form(),
    contrasena: str = Form()
):
    """
    Esta es la ruta de API que tu register.html llama.
    Usa los nombres de tu esquema SQL.
    """
    print(f"🔹 API: Intento de registro para: {correo}")
    conn = None
    
    try:
        # 1. Hashear la contraseña ANTES de guardarla
        hashed_password = pwd_context.hash(contrasena)
        
        # 2. Conectarse a la BD
        conn = db_connect.get_connection()
        if conn is None:
            return JSONResponse({"error": "Error de conexión con la base de datos"}, status_code=500)
        
        cursor = conn.cursor()
        
        # 3. Ejecutar el INSERT
        # Usamos los nombres de tu tabla: usuarios, nombre, apellido, email, curp, contrasena_hash, rol, saldo_total
        # El rol por defecto es 'usuario' y el saldo 0.
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, apellido, email, curp, contrasena_hash, rol, saldo_total)
            VALUES (%s, %s, %s, %s, %s, 'usuario', 0.00)
            """,
            (nombre, apellido, correo, curp, hashed_password)
        )
        
        # 4. Confirmar la transacción
        conn.commit()
        
        print(f"✅ API: Registro exitoso para {correo}")
        return JSONResponse({"success": True, "message": "Usuario registrado exitosamente"})

    except psycopg2.errors.UniqueViolation as e:
        # Error específico si el email o curp ya existen (si los tienes como UNIQUE en tu BD)
        conn.rollback() # Revertir la transacción
        print(f"❌ API: Conflicto de datos (email o curp ya existen): {e}")
        return JSONResponse({"error": "El correo electrónico o la CURP ya están registrados."}, status_code=409)
        
    except Exception as e:
        if conn:
            conn.rollback() # Revertir en caso de cualquier otro error
        print(f"🚨 API ERROR (Register): {e}")
        return JSONResponse({"error": f"Error interno del servidor: {e}"}, status_code=500)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
