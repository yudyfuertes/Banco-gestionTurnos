from flask import Flask, jsonify, request
import requests, os, pybreaker
from database import conectar

app = Flask(__name__)

circuito_turnos = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False
)

estados_validos = ["enviada", "leida"]


@app.route("/notificaciones", methods=["GET"])
def listar():
    turno_id = request.args.get("turno_id")
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    if turno_id:
        cursor.execute("SELECT * FROM notificaciones WHERE turno_id = %s", (turno_id,))
    else:
        cursor.execute("SELECT * FROM notificaciones")
    notificaciones = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(notificaciones)


@app.route("/notificaciones/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        SELECT * FROM notificaciones
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    notificacion = cursor.fetchone()
    cursor.close()
    conexion.close()
    if notificacion is None:
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    return jsonify(notificacion)


@app.route("/notificaciones", methods=["POST"])
def crear():
    nuevaNotificacion = request.json
    if "turno_id" not in nuevaNotificacion:
        return jsonify({"mensaje": "El campo turno_id es obligatorio"}), 400
    tiempo_maximo = float(os.getenv("TURNOS_TIMEOUT", "2"))
    url = os.getenv("TURNOS_URL") + "/turnos/" + str(nuevaNotificacion["turno_id"]) + "/detalle"
    try:
        with circuito_turnos.calling():
            respuesta = requests.get(url, timeout=tiempo_maximo)
            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "Circuito abierto: Turnos no disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servicio de turnos no responde"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "No se pudo conectar con el servicio de turnos"}), 503
    except requests.exceptions.HTTPError:
        return jsonify({"mensaje": "Error en el servicio de turnos"}), 502

    if respuesta.status_code == 404:
        return jsonify({"mensaje": "Turno no encontrado"}), 404
    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error en el servicio de turnos"}), 502

    detalle = respuesta.json()
    if detalle["asesor"] is None:
        return jsonify({"mensaje": "El turno aún no tiene ventanilla asignada"}), 409

    texto = (
        "Turno " + detalle["turno"]["codigo"] + " - " + detalle["cliente"]["nombre"]
        + ": diríjase a la ventanilla " + str(detalle["asesor"]["ventanilla"])
    )

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        INSERT INTO notificaciones
        (turno_id, texto)
        VALUES (%s, %s)
    """
    valores = (nuevaNotificacion["turno_id"], texto)
    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Notificación creada", "id": nuevo_id}), 201


@app.route("/notificaciones/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.json
    for campo in ["turno_id", "texto", "estado"]:
        if campo not in datos:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    if datos["estado"] not in estados_validos:
        return jsonify({"mensaje": "Estado inválido"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM notificaciones WHERE id = %s", (id,))
    notificacion = cursor.fetchone()
    if notificacion is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    sql = """
        UPDATE notificaciones
        SET turno_id = %s, texto = %s, estado = %s WHERE id = %s
    """
    valores = (datos["turno_id"], datos["texto"], datos["estado"], id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Notificación actualizada"})


@app.route("/notificaciones/<int:id>", methods=["PATCH"])
def modificar(id):
    datos = request.json
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM notificaciones WHERE id = %s", (id,))
    notificacion = cursor.fetchone()
    if notificacion is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    texto = datos.get("texto", notificacion["texto"])
    estado = datos.get("estado", notificacion["estado"])
    if estado not in estados_validos:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Estado inválido"}), 400
    sql = """
        UPDATE notificaciones
        SET texto = %s, estado = %s WHERE id = %s
    """
    valores = (texto, estado, id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Notificación modificada"})


@app.route("/notificaciones/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM notificaciones WHERE id = %s", (id,))
    notificacion = cursor.fetchone()
    if notificacion is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Notificación no encontrada"}), 404
    cursor.execute(
        "DELETE FROM notificaciones WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Notificación eliminada"})


@app.route("/notificaciones/circuito/turnos", methods=["GET"])
def estado_circuito():
    return jsonify({
        "estado": circuito_turnos.current_state.upper(),
        "fallos_consecutivos": circuito_turnos.fail_counter,
        "umbral_fallas": circuito_turnos.fail_max,
        "periodo_recuperacion": circuito_turnos.reset_timeout
    }), 200


app.run(host="0.0.0.0", port=5000)
