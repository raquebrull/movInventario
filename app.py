from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import os

app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas

def get_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={os.environ['DB_SERVER']};DATABASE={os.environ['DB_NAME']};UID={os.environ['DB_USER']};PWD={os.environ['DB_PASS']}"
    )

@app.route('/')
def home():
    return 'API en línea'

@app.route('/consulta', methods=['GET'])
def consulta():
    conn = get_connection()
    cursor = conn.cursor()

    fechaD = request.args.get('fechaD')
    fechaH = request.args.get('fechaH')
    almacen = request.args.get('almacen', '')
    CC = request.args.get('CC', '')
    TipoDiario = request.args.get('TipoDiario', '')
    GrupoArti = request.args.get('GrupoArti', '')

    cursor.execute("EXEC SP_ConsultaMovInventario ?, ?, ?, ?, ?, ?", fechaD, fechaH, almacen, CC, TipoDiario, GrupoArti)
    columnas = [col[0] for col in cursor.description]
    resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

    return jsonify(resultados)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render pasa el puerto en la variable de entorno PORT
    app.run(host='0.0.0.0', port=port)
