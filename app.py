from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import os

app = Flask(__name__)
# Habilita CORS para todas las rutas. En producción, considera restringir esto a dominios específicos.
CORS(app)

def get_connection():
    """
    Establece y retorna una conexión a la base de datos SQL Server
    utilizando variables de entorno para las credenciales.
    """
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={os.environ['DB_SERVER']};DATABASE={os.environ['DB_NAME']};UID={os.environ['DB_USER']};PWD={os.environ['DB_PASS']}"
        )
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # Puedes loguear el error aquí para depuración
        print(f"Error al conectar a la base de datos: {sqlstate} - {ex}")
        raise ConnectionError("No se pudo conectar a la base de datos.")

@app.route('/')
def home():
    """
    Ruta de inicio para verificar si la API está en línea.
    """
    return 'API de Consulta de Movimiento de Inventario en línea'

@app.route('/consulta', methods=['POST']) # <--- CAMBIO CLAVE: Cambiado a POST
def consulta():
    """
    Endpoint para consultar el movimiento de inventario.
    Espera un cuerpo JSON con los parámetros del procedimiento almacenado.
    """
    # Verifica que la solicitud sea JSON
    if not request.is_json:
        return jsonify({"error": "Content-Type debe ser application/json"}), 400

    # Accede a los datos del cuerpo JSON de la solicitud
    data = request.get_json()

    # Extrae los parámetros, proporcionando valores por defecto si no están presentes
    # Asegúrate de que los nombres de las claves coincidan con los que envía tu frontend
    fechaD = data.get('fechaD')
    fechaH = data.get('fechaH')
    almacen = data.get('almacen', '')
    CC = data.get('CC', '')
    TipoDiario = data.get('TipoDiario', '')
    GrupoArti = data.get('GrupoArti', '')

    # Validación básica de parámetros requeridos
    if not fechaD or not fechaH:
        return jsonify({"error": "Las fechas de inicio y fin (fechaD, fechaH) son requeridas."}), 400

    conn = None # Inicializa conn a None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Ejecuta el procedimiento almacenado
        cursor.execute("EXEC SP_ConsultaMovInventario ?, ?, ?, ?, ?, ?",
                       fechaD, fechaH, almacen, CC, TipoDiario, GrupoArti)

        # Obtiene los nombres de las columnas
        columnas = [col[0] for col in cursor.description]
        # Obtiene todos los resultados y los convierte en una lista de diccionarios
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        return jsonify(resultados)

    except ConnectionError as e:
        # Error de conexión a la base de datos
        return jsonify({"error": str(e)}), 500
    except pyodbc.Error as ex:
        # Errores específicos de la base de datos
        sqlstate = ex.args[0]
        # Puedes loguear el error aquí para depuración
        print(f"Error de base de datos: {sqlstate} - {ex}")
        return jsonify({"error": f"Error en la base de datos: {ex}"}), 500
    except Exception as e:
        # Otros errores inesperados
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Ocurrió un error inesperado: {e}"}), 500
    finally:
        # Asegura que la conexión se cierre
        if conn:
            conn.close()

if __name__ == '__main__':
    # Render pasa el puerto en la variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
