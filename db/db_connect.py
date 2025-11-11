import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",   # pon tu contraseña si tienes
            database="royalcrumbs"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("❌ Error al conectar:", e)
        return None


# ======================================
# ✅ PRUEBA DIRECTA DE CONEXIÓN LOCAL
# ======================================
if __name__ == "__main__":
    connection = get_connection()
    if connection:
        print("✅ Conexión establecida correctamente")
        connection.close()
    else:
        print("❌ Error: no se pudo conectar a la base de datos")
