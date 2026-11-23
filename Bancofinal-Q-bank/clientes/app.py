from flask import Flask, jsonify, request
import requests, os, pybreaker
from database import conectar

app = Flask(__name__)

circuito_turnos = pybreaker.CircuitBreaker(
    fail_max=int(os.getenv("CB_MAX_FALLOS", "3")),
    reset_timeout=int(os.getenv("CB_RECUPERACION", "30")),
    throw_new_error_on_trip=False
)


@app.route("/clientes", methods=["GET"])
def listar():
    documento = request.args.get("documento")
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    if documento:
        cursor.execute("SELECT * FROM clientes WHERE documento = %s", (documento,))
    else:
        cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(clientes)


@app.route("/clientes/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    sql = """
        SELECT * FROM clientes
        WHERE id = %s
    """
    cursor.execute(sql, (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()
    if cliente is None:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    return jsonify(cliente)


@app.route("/clientes", methods=["POST"])
def crear():
    nuevoCliente = request.json
    for campo in ["nombre", "documento"]:
        if campo not in nuevoCliente:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE documento = %s", (nuevoCliente["documento"],))
    repetido = cursor.fetchone()
    if repetido is not None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "El documento ya está registrado"}), 409
    sql = """
        INSERT INTO clientes
        (nombre, documento, telefono)
        VALUES (%s, %s, %s)
    """
    valores = (
        nuevoCliente["nombre"], nuevoCliente["documento"], nuevoCliente.get("telefono")
    )
    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Cliente creado", "id": nuevo_id}), 201


@app.route("/clientes/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.json
    for campo in ["nombre", "documento", "telefono"]:
        if campo not in datos:
            return jsonify({"mensaje": "El campo " + campo + " es obligatorio"}), 400
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    cursor.execute(
        "SELECT * FROM clientes WHERE documento = %s AND id != %s", (datos["documento"], id))
    repetido = cursor.fetchone()
    if repetido is not None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "El documento ya está registrado"}), 409
    sql = """
        UPDATE clientes
        SET nombre = %s, documento = %s, telefono = %s WHERE id = %s
    """
    valores = (datos["nombre"], datos["documento"], datos["telefono"], id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Cliente actualizado"})


@app.route("/clientes/<int:id>", methods=["PATCH"])
def modificar(id):
    datos = request.json
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    nombre = datos.get("nombre", cliente["nombre"])
    documento = datos.get("documento", cliente["documento"])
    telefono = datos.get("telefono", cliente["telefono"])
    cursor.execute(
        "SELECT * FROM clientes WHERE documento = %s AND id != %s", (documento, id))
    repetido = cursor.fetchone()
    if repetido is not None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "El documento ya está registrado"}), 409
    sql = """
        UPDATE clientes
        SET nombre = %s, documento = %s, telefono = %s WHERE id = %s
    """
    valores = (nombre, documento, telefono, id)
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Cliente modificado"})


@app.route("/clientes/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    if cliente is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    cursor.execute(
        "DELETE FROM clientes WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"mensaje": "Cliente eliminado"})


@app.route("/clientes/<int:id>/solicitar-turno", methods=["POST"])
def solicitar_turno(id):
    datos = request.json
    tramite = datos.get("tramite", "general")
    tiempo_maximo = float(os.getenv("TURNOS_TIMEOUT", "2"))
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()
    if cliente is None:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    url = os.getenv("TURNOS_URL") + "/turnos"
    try:
        with circuito_turnos.calling():
            respuesta = requests.post(
                url, json={"cliente_id": id, "tramite": tramite}, timeout=tiempo_maximo)
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

    if respuesta.status_code != 201:
        return jsonify({"mensaje": "Error en el servicio de turnos"}), 502
    return jsonify(respuesta.json()), 201


@app.route("/clientes/circuito/turnos", methods=["GET"])
def estado_circuito():
    return jsonify({
        "estado": circuito_turnos.current_state.upper(),
        "fallos_consecutivos": circuito_turnos.fail_counter,
        "umbral_fallas": circuito_turnos.fail_max,
        "periodo_recuperacion": circuito_turnos.reset_timeout
    }), 200


app.run(host="0.0.0.0", port=5000)
