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

@app.get("/asesores")
def listar():
    return jsonify(consultar("SELECT * FROM asesores"))


@app.get("/asesores/<int:id>")
def obtener(id):
    filas = consultar("SELECT * FROM asesores WHERE id=%s", (id,))
    if not filas:
        return error("Asesor no encontrado", 404)
    return jsonify(filas[0])


@app.post("/asesores")
def crear():
    datos = request.get_json(silent=True) or {}
    if not datos.get("nombre") or datos.get("ventanilla") is None:
        return error("nombre y ventanilla son obligatorios", 400)
    ejecutar(
        "INSERT INTO asesores (nombre, ventanilla, estado) VALUES (%s, %s, %s)",
        (datos["nombre"], datos["ventanilla"], datos.get("estado", "disponible")),
    )
    asesor = consultar("SELECT * FROM asesores ORDER BY id DESC LIMIT 1")[0]
    return jsonify(asesor), 201


@app.put("/asesores/<int:id>")
def actualizar(id):
    filas = consultar("SELECT * FROM asesores WHERE id=%s", (id,))
    if not filas:
        return error("Asesor no encontrado", 404)
    actual = filas[0]
    datos = request.get_json(silent=True) or {}
    ejecutar(
        "UPDATE asesores SET nombre=%s, ventanilla=%s, estado=%s WHERE id=%s",
        (datos.get("nombre", actual["nombre"]),
        datos.get("ventanilla", actual["ventanilla"]),
        datos.get("estado", actual["estado"]), id),
    )
    return jsonify(consultar("SELECT * FROM asesores WHERE id=%s", (id,))[0])


@app.delete("/asesores/<int:id>")
def eliminar(id):
    if not consultar("SELECT * FROM asesores WHERE id=%s", (id,)):
        return error("Asesor no encontrado", 404)
    ejecutar("DELETE FROM asesores WHERE id=%s", (id,))
    return jsonify({"mensaje": "Asesor eliminado"})

@app.put("/asesores/<int:id>/atender-turno/<int:turno_id>")
def atender_turno(id, turno_id):
    filas = consultar("SELECT * FROM asesores WHERE id=%s", (id,))
    if not filas:
        return error("Asesor no encontrado", 404)

    datos = request.get_json(silent=True) or {}
    payload = {
        "asesor_id": id,
        "estado": datos.get("estado", "en_atencion")
    }

    try:
        resp = requests.put(f"{TURNOS_URL}/turnos/{turno_id}", json=payload, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException:
        return error("Servicio de turnos no disponible", 503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")))
