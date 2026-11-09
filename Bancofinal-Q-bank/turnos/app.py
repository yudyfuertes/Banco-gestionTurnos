import os
import time
import pybreaker
import requests
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


def conectar():
    for intento in range(10):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", "3306")),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )
        except mysql.connector.Error as e:
            print(f"La base de datos aún está cargando. Intento {intento + 1}/10")
            print(e)
            time.sleep(3)
    raise Exception("No fue posible conectar con MySQL después de 10 intentos")


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


HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "2"))
circuito_clientes = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False,
)
circuito_asesores = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False,
)


def pedir(circuito, url):
    
    try:
        with circuito.calling():
            r = requests.get(url, timeout=HTTP_TIMEOUT)
            if r.status_code >= 500:
                r.raise_for_status()
    except pybreaker.CircuitBreakerError:
        return None, "circuito_abierto"
    except requests.exceptions.Timeout:
        return None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, "caido"
    except requests.exceptions.HTTPError:
        return None, "error_servidor"
    if r.status_code == 200:
        return r.json(), "ok"
    if r.status_code == 404:
        return None, "no_existe"
    return None, "error_servidor"


def error_por_estado(estado, recurso):
    if estado == "timeout":
        return error(f"El servicio de {recurso} no responde", 504)
    if estado == "circuito_abierto":
        return error(f"Circuito abierto: servicio de {recurso} no disponible", 503)
    if estado == "caido":
        return error(f"Servicio de {recurso} no disponible", 503)
    if estado == "error_servidor":
        return error(f"Error en el servicio de {recurso}", 502)
    return None


def validar(circuito, base_url, recurso, id, nombre):

    _, estado = pedir(circuito, f"{base_url}/{recurso}/{id}")
    if estado == "no_existe":
        return error(f"{nombre} inexistente", 404)
    return error_por_estado(estado, recurso)


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
    err = validar(circuito_clientes, CLIENTES_URL, "clientes", datos["cliente_id"], "Cliente")
    if err:
        return err
    asesor_id = datos.get("asesor_id")
    if asesor_id:
        err = validar(circuito_asesores, ASESORES_URL, "asesores", asesor_id, "Asesor")
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
        err = validar(circuito_asesores, ASESORES_URL, "asesores", asesor_id, "Asesor")
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

    cliente, estado = pedir(circuito_clientes, f"{CLIENTES_URL}/clientes/{turno['cliente_id']}")
    err = error_por_estado(estado, "clientes")
    if err:
        return err
    asesor = None
    if turno["asesor_id"]:
        asesor, estado = pedir(circuito_asesores, f"{ASESORES_URL}/asesores/{turno['asesor_id']}")
        err = error_por_estado(estado, "asesores")
        if err:
            return err
    turno["cliente"] = cliente
    turno["asesor"] = asesor
    return jsonify(turno)



@app.get("/turnos/circuito")
def estado_circuito():
    return jsonify({
        "clientes": {
            "estado": circuito_clientes.current_state.upper(),
            "fallos_consecutivos": circuito_clientes.fail_counter,
            "periodo_recuperacion": circuito_clientes.reset_timeout,
        },
        "asesores": {
            "estado": circuito_asesores.current_state.upper(),
            "fallos_consecutivos": circuito_asesores.fail_counter,
            "periodo_recuperacion": circuito_asesores.reset_timeout,
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")))
