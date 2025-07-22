from flask import Flask, request, jsonify
import pyodbc
import os

app = Flask(__name__)

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
