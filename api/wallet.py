from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import db_connect
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import decimal # Para manejar el dinero de forma segura

router = APIRouter()

@router.post("/api/wallet/deposit-card")
async def api_deposit_card(
    # Tu HTML ya debe estar enviando esto desde el script
    id_usuario: int = Form(), 
    monto: str = Form(),
    # Los otros campos del formulario no los usamos en el backend
    # pero podemos recibirlos para que no den error
    numero_tarjeta: str = Form(),
    nombre_titular: str = Form(),
    fecha_exp: str = Form(),
    cvv: str = Form()
):
    """
    Ruta para procesar un DEPÓSITO con tarjeta.
    Esto debe ser una TRANSACCIÓN DE BASE DE DATOS.
    """
    print(f"🔹 API: Intento de depósito de ${monto} para usuario: {id_usuario}")
    
    # Validar y convertir el monto
    try:
        monto_decimal = decimal.Decimal(monto)
        if monto_decimal <= 0:
            return JSONResponse({"error": "El monto debe ser positivo."}, status_code=400)
    except Exception:
        return JSONResponse({"error": "Monto inválido."}, status_code=400)
        
    conn = None
    cursor = None
    
    try:
        conn = db_connect.get_connection()
        if conn is None:
            return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        # ¡IMPORTANTE! Iniciamos una transacción.
        cursor = conn.cursor()

        # PASO 1: Registrar la transacción en la tabla 'Transaccion'
        cursor.execute(
            """
            INSERT INTO Transaccion 
                (id_usuario, tipo_transaccion, monto, estado, metodo_pago, fecha_transaccion)
            VALUES 
                (%s, 'Depósito', %s, 'Completada', 'Tarjeta', %s)
            """,
            (id_usuario, monto_decimal, datetime.now())
        )
        
        # PASO 2: Actualizar el saldo del usuario en la tabla 'Saldo'
        cursor.execute(
            """
            UPDATE Saldo
            SET saldo_actual = saldo_actual + %s,
                ultima_actualizacion = %s
            WHERE id_usuario = %s
            """,
            (monto_decimal, datetime.now(), id_usuario)
        )
        
        # Si ambos comandos funcionaron, confirmamos los cambios
        conn.commit()
        
        print(f"✅ API: Depósito exitoso para {id_usuario}")
        return JSONResponse({"success": True, "message": "Depósito realizado con éxito."})

    except Exception as e:
        # Si algo falló, revertimos TODOS los cambios
        if conn: conn.rollback()
        print(f"🚨 API ERROR (Depósito): {e}")
        return JSONResponse({"error": f"Error interno del servidor: {e}"}, status_code=500)
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ==========================================================
#  NUEVA RUTA: GUARDAR MÉTODO DE PAGO (CLABE)
# ==========================================================
@router.post("/api/wallet/save-method-bank")
async def api_save_bank_method(
    id_usuario: int = Form(),
    clabe: str = Form()
):
    """
    Ruta para guardar o actualizar la cuenta CLABE del usuario
    Llamada por: account-bancaria.html
    """
    print(f"🔹 API: Guardando CLABE para usuario: {id_usuario}")
    
    # (Aquí deberías validar que la CLABE tenga 18 dígitos)
    if len(clabe) != 18 or not clabe.isdigit():
        return JSONResponse({"error": "La CLABE debe tener 18 dígitos numéricos."}, status_code=400)
        
    conn = None
    cursor = None
    
    try:
        conn = db_connect.get_connection()
        if conn is None:
            return JSONResponse({"error": "Error de conexión"}, status_code=500)
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Averiguamos el id_metodo para 'Transferencia' (o 'SPEI')
        #    Asumiré que en tu tabla 'Metodo_Pago' tienes uno llamado 'Transferencia'
        cursor.execute("SELECT id_metodo FROM Metodo_Pago WHERE nombre = 'Transferencia'")
        metodo = cursor.fetchone()
        
        if not metodo:
            # ¡Error! No has creado los métodos de pago en tu BD
            print("🚨 API ERROR: No se encontró 'Transferencia' en la tabla Metodo_Pago")
            return JSONResponse({"error": "Configuración del servidor incompleta (M-404)"}, status_code=500)

        id_metodo_pago = metodo['id_metodo']

        # 2. Usamos 'UPSERT' (UPDATE o INSERT)
        # Intenta actualizar el método bancario del usuario. Si no existe, lo crea.
        cursor.execute(
            """
            INSERT INTO Usuario_Metodo_Pago (id_usuario, id_metodo, token_externo, fecha_registro)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_usuario, id_metodo) -- Si ya tiene un método bancario
            DO UPDATE SET token_externo = EXCLUDED.token_externo,
                          fecha_registro = EXCLUDED.fecha_registro
            """,
            (id_usuario, id_metodo_pago, clabe, datetime.now()) # Guardamos la CLABE como 'token_externo'
        )
        
        conn.commit()
        
        print(f"✅ API: CLABE guardada para {id_usuario}")
        return JSONResponse({"success": True, "message": "Método de pago guardado con éxito."})

    except Exception as e:
        if conn: conn.rollback()
        print(f"🚨 API ERROR (Guardar CLABE): {e}")
        return JSONResponse({"error": f"Error interno del servidor: {e}"}, status_code=500)
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
