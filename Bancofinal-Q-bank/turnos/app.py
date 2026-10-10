import os
import requests
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


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


CLIENTES_URL = os.getenv("CLIENTES_URL")
ASESORES_URL = os.getenv("ASESORES_URL")
ESTADOS = ["en_espera", "en_atencion", "atendido", "cancelado"]


def pedir(url):
    """Consulta por REST a otro servicio. Devuelve (datos, estado)
    donde estado es 'ok', 'no_existe' o 'caido'."""
    try:
        r = requests.get(url, timeout=5)
    except requests.RequestException:
        return None, "caido"
    if r.status_code == 200:
        return r.json(), "ok"
    if r.status_code == 404:
        return None, "no_existe"
    return None, "caido"


def validar(base_url, recurso, id, nombre):
    """Devuelve None si existe, o una respuesta de error (404 o 503)."""
    _, estado = pedir(f"{base_url}/{recurso}/{id}")
    if estado == "no_existe":
        return error(f"{nombre} inexistente", 404)
    if estado == "caido":
        return error(f"Servicio de {recurso} no disponible", 503)
    return None


def buscar_turno(id):
    filas = consultar("SELECT * FROM turnos WHERE id=%s", (id,))
    if not filas:
        return None
    turno = filas[0]
    turno["creado"] = str(turno["creado"])
    return turno

@app.get("/turnos")
def listar():
    turnos = consultar("SELECT * FROM turnos")
    for t in turnos:
        t["creado"] = str(t["creado"])
    return jsonify(turnos)


@app.get("/turnos/<int:id>")
def obtener(id):
    turno = buscar_turno(id)
    if not turno:
        return error("Turno no encontrado", 404)
    return jsonify(turno)


@app.post("/turnos")
def crear():
    datos = request.get_json(silent=True) or {}
    if not datos.get("cliente_id"):
        return error("cliente_id es obligatorio", 400)
    err = validar(CLIENTES_URL, "clientes", datos["cliente_id"], "Cliente")
    if err:
        return err
    asesor_id = datos.get("asesor_id")
    if asesor_id:
        err = validar(ASESORES_URL, "asesores", asesor_id, "Asesor")
        if err:
            return err
    ejecutar(
        "INSERT INTO turnos (cliente_id, asesor_id, tramite) VALUES (%s, %s, %s)",
        (datos["cliente_id"], asesor_id, datos.get("tramite", "general")),
    )
    nuevo = consultar("SELECT * FROM turnos ORDER BY id DESC LIMIT 1")[0]
    ejecutar("UPDATE turnos SET codigo=%s WHERE id=%s", (f"T-{nuevo['id']:03d}", nuevo["id"]))
    return jsonify(buscar_turno(nuevo["id"])), 201


@app.put("/turnos/<int:id>")
def actualizar(id):
    actual = buscar_turno(id)
    if not actual:
        return error("Turno no encontrado", 404)
    datos = request.get_json(silent=True) or {}
    estado = datos.get("estado", actual["estado"])
    if estado not in ESTADOS:
        return error("Estado inválido. Use: " + ", ".join(ESTADOS), 400)
    asesor_id = datos.get("asesor_id", actual["asesor_id"])
    if "asesor_id" in datos and asesor_id:
        err = validar(ASESORES_URL, "asesores", asesor_id, "Asesor")
        if err:
            return err
    ejecutar(
        "UPDATE turnos SET estado=%s, asesor_id=%s, tramite=%s WHERE id=%s",
        (estado, asesor_id, datos.get("tramite", actual["tramite"]), id),
    )
    return jsonify(buscar_turno(id))


@app.delete("/turnos/<int:id>")
def eliminar(id):
    if not buscar_turno(id):
        return error("Turno no encontrado", 404)
    ejecutar("DELETE FROM turnos WHERE id=%s", (id,))
    return jsonify({"mensaje": "Turno eliminado"})

@app.get("/turnos/<int:id>/detalle")
def detalle(id):
    turno = buscar_turno(id)
    if not turno:
        return error("Turno no encontrado", 404)
    cliente, estado = pedir(f"{CLIENTES_URL}/clientes/{turno['cliente_id']}")
    if estado == "caido":
        return error("Servicio de clientes no disponible", 503)
    asesor = None
    if turno["asesor_id"]:
        asesor, estado = pedir(f"{ASESORES_URL}/asesores/{turno['asesor_id']}")
        if estado == "caido":
            return error("Servicio de asesores no disponible", 503)
    turno["cliente"] = cliente
    turno["asesor"] = asesor
    return jsonify(turno)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")))
