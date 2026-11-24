from flask import Flask, jsonify, Response, request
import os
import requests

app = Flask(__name__)

CLIENTES_URL = os.getenv("CLIENTES_URL", "http://clientes:5000")
ASESORES_URL = os.getenv("ASESORES_URL", "http://asesores:5000")
TURNOS_URL = os.getenv("TURNOS_URL", "http://turnos:5000")
NOTIFICACIONES_URL = os.getenv("NOTIFICACIONES_URL", "http://notificaciones:5000")


def reenviar(metodo, url):
    try:
        respuesta = requests.request(metodo, url, params=request.args,
                                     json=request.get_json(silent=True), timeout=5)
        return Response(respuesta.content, status=respuesta.status_code,
                        content_type=respuesta.headers.get("Content-Type", "application/json"))
    except requests.exceptions.Timeout:
        return jsonify({
            "mensaje": "El servicio destino tardó en responder"
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "mensaje": "No fue posible conectar con el servicio destino"
        }), 503



@app.after_request
def permitir_navegador(respuesta):
    respuesta.headers["Access-Control-Allow-Origin"] = "*"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    return respuesta




@app.route("/clientes", methods=["GET", "POST"])
def ruta_clientes():
    return reenviar(request.method, CLIENTES_URL + "/clientes")


@app.route("/clientes/<path:ruta>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def ruta_clientes_detalle(ruta):
    return reenviar(request.method, CLIENTES_URL + "/clientes/" + ruta)




@app.route("/asesores", methods=["GET", "POST"])
def ruta_asesores():
    return reenviar(request.method, ASESORES_URL + "/asesores")


@app.route("/asesores/<path:ruta>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def ruta_asesores_detalle(ruta):
    return reenviar(request.method, ASESORES_URL + "/asesores/" + ruta)




@app.route("/turnos", methods=["GET", "POST"])
def ruta_turnos():
    return reenviar(request.method, TURNOS_URL + "/turnos")


@app.route("/turnos/<path:ruta>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def ruta_turnos_detalle(ruta):
    return reenviar(request.method, TURNOS_URL + "/turnos/" + ruta)




@app.route("/notificaciones", methods=["GET", "POST"])
def ruta_notificaciones():
    return reenviar(request.method, NOTIFICACIONES_URL + "/notificaciones")


@app.route("/notificaciones/<path:ruta>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def ruta_notificaciones_detalle(ruta):
    return reenviar(request.method, NOTIFICACIONES_URL + "/notificaciones/" + ruta)


app.run(host="0.0.0.0", port=5000)
