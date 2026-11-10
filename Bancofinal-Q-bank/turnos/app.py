from flask import Flask, jsonify, request
import requests, os, pybreaker
from database import conectar

app = Flask(__name__)

circuito_clientes = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False
)

circuito_asesores = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False
)

estados_validos = ["en_espera", "en_atencion", "atendido", "cancelado"]


@app.route("/turnos", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turnos")
    turnos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(turnos)


@app.route("/turnos/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        SELECT * FROM turnos
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    turno = cursor.fetchone()
    cursor.close()
    conexion.close()
    if turno is None:
        return jsonify({"mensaje": "Turno no encontrado"}), 404
    return jsonify(turno)


@app.route("/turnos", methods=["POST"])
def crear():
    nuevoTurno = request.json
    if "cliente_id" not in nuevoTurno:
        return jsonify({"mensaje": "El campo cliente_id es obligatorio"}), 400
    tramite = nuevoTurno.get("tramite", "general")
    tiempo_maximo = float(os.getenv("CLIENTES_TIMEOUT", "2"))
    url = os.getenv("CLIENTES_URL") + "/clientes/" + str(nuevoTurno["cliente_id"])
    try:
        with circuito_clientes.calling():
            respuesta = requests.get(url, timeout=tiempo_maximo)
            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "Circuito abierto: Clientes no disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servicio de clientes no responde"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "No se pudo conectar con el servicio de clientes"}), 503
    except requests.exceptions.HTTPError:
        return jsonify({"mensaje": "Error en el servicio de clientes"}), 502

    if respuesta.status_code == 404:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error en el servicio de clientes"}), 502

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        INSERT INTO turnos
        (cliente_id, tramite)
        VALUES (%s, %s)
    """
    valores = (nuevoTurno["cliente_id"], tramite)
    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    codigo = "T-" + str(nuevo_id).zfill(3)
    cursor.execute(
        "UPDATE turnos SET codigo = %s WHERE id = %s", (codigo, nuevo_id))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Turno creado", "id": nuevo_id, "codigo": codigo}), 201


@app.route("/turnos/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.json
    for campo in ["tramite", "estado", "asesor_id"]:
        if campo not in datos:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    if datos["estado"] not in estados_validos:
        return jsonify({"mensaje": "Estado inválido"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM turnos WHERE id = %s", (id,))
    turno = cursor.fetchone()
    if turno is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Turno no encontrado"}), 404
    sql = """
        UPDATE turnos
        SET tramite = %s, estado = %s, asesor_id = %s WHERE id = %s
    """
    valores = (datos["tramite"], datos["estado"], datos["asesor_id"], id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Turno actualizado"})


@app.route("/turnos/<int:id>", methods=["PATCH"])
def modificar(id):
    datos = request.json
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM turnos WHERE id = %s", (id,))
    turno = cursor.fetchone()
    if turno is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Turno no encontrado"}), 404
    tramite = datos.get("tramite", turno["tramite"])
    estado = datos.get("estado", turno["estado"])
    asesor_id = datos.get("asesor_id", turno["asesor_id"])
    if estado not in estados_validos:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Estado inválido"}), 400
    sql = """
        UPDATE turnos
        SET tramite = %s, estado = %s, asesor_id = %s WHERE id = %s
    """
    valores = (tramite, estado, asesor_id, id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({
        "mensaje": "Turno modificado",
        "id": id,
        "estado": estado,
        "asesor_id": asesor_id
    })


@app.route("/turnos/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM turnos WHERE id = %s", (id,))
    turno = cursor.fetchone()
    if turno is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Turno no encontrado"}), 404
    cursor.execute(
        "DELETE FROM turnos WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Turno eliminado"})


@app.route("/turnos/<int:id>/detalle", methods=["GET"])
def detalle(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM turnos WHERE id = %s", (id,))
    turno = cursor.fetchone()
    cursor.close()
    conexion.close()
    if turno is None:
        return jsonify({"mensaje": "Turno no encontrado"}), 404

    # Turnos -> Clientes
    tiempo_maximo = float(os.getenv("CLIENTES_TIMEOUT", "2"))
    url = os.getenv("CLIENTES_URL") + "/clientes/" + str(turno["cliente_id"])
    try:
        with circuito_clientes.calling():
            respuesta = requests.get(url, timeout=tiempo_maximo)
            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
    except pybreaker.CircuitBreakerError:
        return jsonify({"mensaje": "Circuito abierto: Clientes no disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "El servicio de clientes no responde"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "No se pudo conectar con el servicio de clientes"}), 503
    except requests.exceptions.HTTPError:
        return jsonify({"mensaje": "Error en el servicio de clientes"}), 502

    if respuesta.status_code == 404:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    if respuesta.status_code != 200:
        return jsonify({"mensaje": "Error en el servicio de clientes"}), 502
    cliente = respuesta.json()

 
    asesor = None
    if turno["asesor_id"] is not None:
        tiempo_maximo = float(os.getenv("ASESORES_TIMEOUT", "2"))
        url = os.getenv("ASESORES_URL") + "/asesores/" + str(turno["asesor_id"])
        try:
            with circuito_asesores.calling():
                respuesta = requests.get(url, timeout=tiempo_maximo)
                if respuesta.status_code >= 500:
                    respuesta.raise_for_status()
        except pybreaker.CircuitBreakerError:
            return jsonify({"mensaje": "Circuito abierto: Asesores no disponible"}), 503
        except requests.exceptions.Timeout:
            return jsonify({"mensaje": "El servicio de asesores no responde"}), 504
        except requests.exceptions.ConnectionError:
            return jsonify({"mensaje": "No se pudo conectar con el servicio de asesores"}), 503
        except requests.exceptions.HTTPError:
            return jsonify({"mensaje": "Error en el servicio de asesores"}), 502

        if respuesta.status_code == 404:
            return jsonify({"mensaje": "Asesor no encontrado"}), 404
        if respuesta.status_code != 200:
            return jsonify({"mensaje": "Error en el servicio de asesores"}), 502
        asesor = respuesta.json()

    return jsonify({
        "turno": turno,
        "cliente": cliente,
        "asesor": asesor
    }), 200


@app.route("/turnos/circuito/clientes", methods=["GET"])
def estado_circuito_clientes():
    return jsonify({
        "estado": circuito_clientes.current_state.upper(),
        "fallos_consecutivos": circuito_clientes.fail_counter,
        "umbral_fallas": circuito_clientes.fail_max,
        "periodo_recuperacion": circuito_clientes.reset_timeout
    }), 200


@app.route("/turnos/circuito/asesores", methods=["GET"])
def estado_circuito_asesores():
    return jsonify({
        "estado": circuito_asesores.current_state.upper(),
        "fallos_consecutivos": circuito_asesores.fail_counter,
        "umbral_fallas": circuito_asesores.fail_max,
        "periodo_recuperacion": circuito_asesores.reset_timeout
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
