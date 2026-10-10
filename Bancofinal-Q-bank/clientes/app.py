import os
import requests
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

TURNOS_URL = os.getenv("TURNOS_URL", "http://turnos:5003")


def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def consultar(sql, valores=None):
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, valores)
    filas = cur.fetchall()
    conn.close()
    return filas


def ejecutar(sql, valores=None):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(sql, valores)
    conn.commit()
    conn.close()


def error(msg, codigo):
    return jsonify({"error": msg}), codigo

@app.get("/clientes")
def listar():
    return jsonify(consultar("SELECT * FROM clientes"))


@app.get("/clientes/<int:id>")
def obtener(id):
    filas = consultar("SELECT * FROM clientes WHERE id=%s", (id,))
    if not filas:
        return error("Cliente no encontrado", 404)
    return jsonify(filas[0])


@app.post("/clientes")
def crear():
    datos = request.get_json(silent=True) or {}
    if not datos.get("nombre") or not datos.get("documento"):
        return error("nombre y documento son obligatorios", 400)
    try:
        ejecutar(
            "INSERT INTO clientes (nombre, documento, telefono) VALUES (%s, %s, %s)",
            (datos["nombre"], datos["documento"], datos.get("telefono")),
        )
    except mysql.connector.IntegrityError:
        return error("El documento ya está registrado", 409)
    cliente = consultar("SELECT * FROM clientes WHERE documento=%s", (datos["documento"],))[0]
    return jsonify(cliente), 201


@app.put("/clientes/<int:id>")
def actualizar(id):
    filas = consultar("SELECT * FROM clientes WHERE id=%s", (id,))
    if not filas:
        return error("Cliente no encontrado", 404)
    actual = filas[0]
    datos = request.get_json(silent=True) or {}
    try:
        ejecutar(
            "UPDATE clientes SET nombre=%s, documento=%s, telefono=%s WHERE id=%s",
            (datos.get("nombre", actual["nombre"]),
            datos.get("documento", actual["documento"]),
            datos.get("telefono", actual["telefono"]), id),
        )
    except mysql.connector.IntegrityError:
        return error("El documento ya está registrado", 409)
    return jsonify(consultar("SELECT * FROM clientes WHERE id=%s", (id,))[0])


@app.delete("/clientes/<int:id>")
def eliminar(id):
    if not consultar("SELECT * FROM clientes WHERE id=%s", (id,)):
        return error("Cliente no encontrado", 404)
    ejecutar("DELETE FROM clientes WHERE id=%s", (id,))
    return jsonify({"mensaje": "Cliente eliminado"})

@app.post("/clientes/<int:id>/solicitar-turno")
def solicitar_turno(id):
    filas = consultar("SELECT * FROM clientes WHERE id=%s", (id,))
    if not filas:
        return error("Cliente no encontrado", 404)

    datos = request.get_json(silent=True) or {}
    payload = {
        "cliente_id": id,
        "tramite": datos.get("tramite", "general")
    }

    try:
        resp = requests.post(f"{TURNOS_URL}/turnos", json=payload, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException:
        return error("Servicio de turnos no disponible", 503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))
