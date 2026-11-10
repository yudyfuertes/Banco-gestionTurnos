from flask import Flask, jsonify, request
import requests, os, pybreaker
from database import conectar

app = Flask(__name__)

circuito_turnos = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False
)


@app.route("/asesores", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM asesores")
    asesores = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(asesores)


@app.route("/asesores/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        SELECT * FROM asesores
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    asesor = cursor.fetchone()
    cursor.close()
    conexion.close()
    if asesor is None:
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    return jsonify(asesor)


@app.route("/asesores", methods=["POST"])
def crear():
    nuevoAsesor = request.json
    for campo in ["nombre", "ventanilla"]:
        if campo not in nuevoAsesor:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        INSERT INTO asesores
        (nombre, ventanilla, estado)
        VALUES (%s, %s, %s)
    """
    valores = (
        nuevoAsesor["nombre"], nuevoAsesor["ventanilla"], nuevoAsesor.get("estado", "disponible")
    )
    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Asesor creado", "id": nuevo_id}), 201


@app.route("/asesores/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.json
    for campo in ["nombre", "ventanilla", "estado"]:
        if campo not in datos:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM asesores WHERE id = %s", (id,))
    asesor = cursor.fetchone()
    if asesor is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    sql = """
        UPDATE asesores
        SET nombre = %s, ventanilla = %s, estado = %s WHERE id = %s
    """
    valores = (datos["nombre"], datos["ventanilla"], datos["estado"], id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Asesor actualizado"})


@app.route("/asesores/<int:id>", methods=["PATCH"])
def modificar(id):
    datos = request.json
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM asesores WHERE id = %s", (id,))
    asesor = cursor.fetchone()
    if asesor is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    nombre = datos.get("nombre", asesor["nombre"])
    ventanilla = datos.get("ventanilla", asesor["ventanilla"])
    estado = datos.get("estado", asesor["estado"])
    sql = """
        UPDATE asesores
        SET nombre = %s, ventanilla = %s, estado = %s WHERE id = %s
    """
    valores = (nombre, ventanilla, estado, id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Asesor modificado"})


@app.route("/asesores/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM asesores WHERE id = %s", (id,))
    asesor = cursor.fetchone()
    if asesor is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    cursor.execute(
        "DELETE FROM asesores WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Asesor eliminado"})


@app.route("/asesores/<int:id>/atender-turno/<int:turno_id>", methods=["PUT"])
def atender_turno(id, turno_id):
    tiempo_maximo = float(os.getenv("TURNOS_TIMEOUT", "2"))
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM asesores WHERE id = %s", (id,))
    asesor = cursor.fetchone()
    cursor.close()
    conexion.close()
    if asesor is None:
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    if asesor["estado"] == "ocupado":
        return jsonify({"mensaje": "El asesor ya está atendiendo un turno"}), 409
    url = os.getenv("TURNOS_URL") + "/turnos/" + str(turno_id)
    try:
        with circuito_turnos.calling():
            respuesta = requests.patch(
                url, json={"asesor_id": id, "estado": "en_atencion"}, timeout=tiempo_maximo)
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
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "UPDATE asesores SET estado = 'ocupado' WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Turno en atención", "turno": respuesta.json()}), 200


@app.route("/asesores/<int:id>/finalizar-turno/<int:turno_id>", methods=["PUT"])
def finalizar_turno(id, turno_id):
    tiempo_maximo = float(os.getenv("TURNOS_TIMEOUT", "2"))
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM asesores WHERE id = %s", (id,))
    asesor = cursor.fetchone()
    cursor.close()
    conexion.close()
    if asesor is None:
        return jsonify({"mensaje": "Asesor no encontrado"}), 404
    url = os.getenv("TURNOS_URL") + "/turnos/" + str(turno_id)
    try:
        with circuito_turnos.calling():
            respuesta = requests.patch(
                url, json={"estado": "atendido"}, timeout=tiempo_maximo)
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
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "UPDATE asesores SET estado = 'disponible' WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Turno atendido", "turno": respuesta.json()}), 200


@app.route("/asesores/circuito/turnos", methods=["GET"])
def estado_circuito():
    return jsonify({
        "estado": circuito_turnos.current_state.upper(),
        "fallos_consecutivos": circuito_turnos.fail_counter,
        "umbral_fallas": circuito_turnos.fail_max,
        "periodo_recuperacion": circuito_turnos.reset_timeout
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
