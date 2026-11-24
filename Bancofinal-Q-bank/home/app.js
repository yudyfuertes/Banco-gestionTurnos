// =====================================================
// Q-Bank - Interfaz de CLIENTES
// Solo permite pedir un turno y ver el estado del turno propio.
// Todas las peticiones pasan por el gateway (puerto 5000).
// =====================================================

const API = "http://" + window.location.hostname + ":5000";
const CLAVE = "qbank_mi_turno";

const nombresEstado = {
    en_espera: "En espera",
    en_atencion: "Llamando",
    atendido: "Atendido",
    cancelado: "Cancelado"
};

const nombresTramite = {
    general: "Atención general",
    caja: "Caja",
    credito: "Crédito",
    cuentas: "Cuentas",
    reclamos: "Reclamos"
};

// -----------------------------------------------------
// Utilidades
// -----------------------------------------------------

function $(id) {
    return document.getElementById(id);
}

async function api(ruta, metodo = "GET", cuerpo = null) {
    const opciones = { method: metodo, headers: {} };

    if (cuerpo) {
        opciones.headers["Content-Type"] = "application/json";
        opciones.body = JSON.stringify(cuerpo);
    }

    let respuesta;
    try {
        respuesta = await fetch(API + ruta, opciones);
    } catch (error) {
        $("sin-conexion").classList.remove("oculto");
        return { ok: false, status: 0, datos: { mensaje: "No hay conexión con el servidor" } };
    }

    $("sin-conexion").classList.add("oculto");

    let datos = {};
    try {
        datos = await respuesta.json();
    } catch (error) {
        datos = { mensaje: "Servicio no disponible" };
    }

    return { ok: respuesta.ok, status: respuesta.status, datos: datos };
}

let temporizadorToast = null;

function mostrarMensaje(texto, esError = false) {
    const toast = $("toast");
    toast.textContent = texto;
    toast.className = "toast" + (esError ? " error" : "");
    clearTimeout(temporizadorToast);
    temporizadorToast = setTimeout(() => toast.classList.add("oculto"), 4000);
}

// El turno del cliente se recuerda en este navegador
function leerTurno() {
    try {
        return JSON.parse(localStorage.getItem(CLAVE));
    } catch (error) {
        return null;
    }
}

function guardarTurno(turno) {
    try {
        if (turno) localStorage.setItem(CLAVE, JSON.stringify(turno));
        else localStorage.removeItem(CLAVE);
    } catch (error) {
        // si el navegador no permite guardar, se sigue funcionando sin recordar
    }
}

// -----------------------------------------------------
// Pantalla pública de turnos (lo que se vería en una sucursal)
// -----------------------------------------------------

async function cargarPantalla() {
    const [rAtencion, rEspera, rAsesores] = await Promise.all([
        api("/turnos?estado=en_atencion"),
        api("/turnos?estado=en_espera"),
        api("/asesores")
    ]);

    if (rEspera.ok) {
        $("pantalla-espera").textContent = "Turnos en espera: " + rEspera.datos.length;
    }

    if (!rAtencion.ok || rAtencion.datos.length === 0) {
        $("pantalla-estado").textContent = "● Sin llamados";
        $("pantalla-estado").className = "status inactivo";
        $("pantalla-codigo").textContent = "—";
        $("pantalla-ventanilla").textContent = "—";
        $("pantalla-tramite").textContent = "—";
        return;
    }

    const lista = rAtencion.datos.sort((a, b) => b.id - a.id);
    const turno = lista[0];
    let ventanilla = "—";

    if (rAsesores.ok) {
        const asesor = rAsesores.datos.find((a) => a.id === turno.asesor_id);
        if (asesor) ventanilla = String(asesor.ventanilla).padStart(2, "0");
    }

    $("pantalla-estado").textContent = "● En atención";
    $("pantalla-estado").className = "status";
    $("pantalla-codigo").textContent = turno.codigo;
    $("pantalla-ventanilla").textContent = ventanilla;
    $("pantalla-tramite").textContent = nombresTramite[turno.tramite] || turno.tramite;
}

// -----------------------------------------------------
// Pedir turno
// -----------------------------------------------------

$("t-documento").addEventListener("change", async () => {
    const documento = $("t-documento").value.trim();
    if (documento === "") return;

    const r = await api("/clientes?documento=" + encodeURIComponent(documento));

    if (r.ok && r.datos.length > 0) {
        $("t-nombre").value = r.datos[0].nombre;
        $("t-telefono").value = r.datos[0].telefono || "";
        $("t-nota").textContent = "Hola de nuevo, " + r.datos[0].nombre;
        $("t-nota").className = "nota ok";
    } else {
        $("t-nota").textContent = "";
        $("t-nota").className = "nota";
    }
});

$("form-turno").addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const documento = $("t-documento").value.trim();
    const nombre = $("t-nombre").value.trim();
    const telefono = $("t-telefono").value.trim();
    const tramite = $("t-tramite").value;

    $("t-boton").disabled = true;
    $("t-boton").textContent = "Pidiendo turno...";

    // 1. Buscar al cliente por documento; si no existe, registrarlo
    const rBuscar = await api("/clientes?documento=" + encodeURIComponent(documento));
    if (!rBuscar.ok) {
        terminarSolicitud(rBuscar.datos.mensaje, true);
        return;
    }

    let clienteId;

    if (rBuscar.datos.length > 0) {
        clienteId = rBuscar.datos[0].id;
    } else {
        const rNuevo = await api("/clientes", "POST", {
            nombre: nombre,
            documento: documento,
            telefono: telefono
        });

        if (!rNuevo.ok) {
            terminarSolicitud(rNuevo.datos.mensaje, true);
            return;
        }
        clienteId = rNuevo.datos.id;
    }

    // 2. Clientes le pide a Turnos que cree el turno
    const rTurno = await api("/clientes/" + clienteId + "/solicitar-turno", "POST", {
        tramite: tramite
    });

    if (!rTurno.ok) {
        terminarSolicitud(rTurno.datos.mensaje, true);
        return;
    }

    guardarTurno({ id: rTurno.datos.id, codigo: rTurno.datos.codigo });

    $("ticket").classList.remove("vacio");
    $("ticket-codigo").textContent = rTurno.datos.codigo;
    $("ticket-mensaje").textContent = "Guarda este código. Sigue tu turno en la sección Mi turno.";

    $("form-turno").reset();
    terminarSolicitud("Tu turno es " + rTurno.datos.codigo, false);

    actualizarMiTurno();
    cargarPantalla();
    $("mi-turno").scrollIntoView();
});

function terminarSolicitud(mensaje, esError) {
    $("t-boton").disabled = false;
    $("t-boton").textContent = "Pedir turno";
    $("t-nota").textContent = mensaje;
    $("t-nota").className = "nota " + (esError ? "error" : "ok");
    mostrarMensaje(mensaje, esError);
}

// -----------------------------------------------------
// Mi turno
// -----------------------------------------------------

async function actualizarMiTurno() {
    const guardado = leerTurno();

    if (!guardado) {
        $("mi-turno-caja").classList.add("oculto");
        $("mi-turno-vacio").classList.remove("oculto");
        $("consulta").classList.remove("oculto");
        return;
    }

    const r = await api("/turnos/" + guardado.id);

    // Si mientras tanto el cliente cambió o borró su turno, esta respuesta ya no sirve
    const vigente = leerTurno();
    if (!vigente || vigente.id !== guardado.id) return;

    if (r.status === 404) {
        guardarTurno(null);
        actualizarMiTurno();
        return;
    }

    if (!r.ok) return;

    const turno = r.datos;

    $("mi-turno-vacio").classList.add("oculto");
    $("consulta").classList.add("oculto");
    $("mi-turno-caja").classList.remove("oculto");

    $("mi-codigo").textContent = turno.codigo;
    $("mi-estado").textContent = nombresEstado[turno.estado] || turno.estado;
    $("mi-estado").className = "etiqueta e-" + turno.estado;
    $("mi-aviso").classList.add("oculto");
    $("btn-cancelar").classList.add("oculto");
    $("btn-nuevo").classList.add("oculto");

    const tramite = nombresTramite[turno.tramite] || turno.tramite;

    if (turno.estado === "en_espera") {
        const rEspera = await api("/turnos?estado=en_espera");
        let antes = 0;
        if (rEspera.ok) {
            antes = rEspera.datos.filter((t) => t.id < turno.id).length;
        }

        $("mi-detalle").textContent =
            tramite + ". Hay " + antes + " turno(s) antes que el tuyo. Te avisaremos cuando sea tu turno.";
        $("btn-cancelar").classList.remove("oculto");
    }

    if (turno.estado === "en_atencion") {
        $("mi-detalle").textContent = tramite + ". Ya es tu turno.";

        const rDetalle = await api("/turnos/" + turno.id + "/detalle");
        const rNotificacion = await api("/notificaciones?turno_id=" + turno.id);

        let textoAviso = "Dirígete a la ventanilla";
        if (rNotificacion.ok && rNotificacion.datos.length > 0) {
            textoAviso = rNotificacion.datos[rNotificacion.datos.length - 1].texto;
        }

        $("mi-aviso-texto").textContent = textoAviso;

        if (rDetalle.ok && rDetalle.datos.asesor) {
            $("mi-ventanilla").textContent = "Ventanilla " + rDetalle.datos.asesor.ventanilla;
            $("mi-asesor").textContent = "Te atiende " + rDetalle.datos.asesor.nombre;
        } else {
            $("mi-ventanilla").textContent = "Dirígete a tu ventanilla";
            $("mi-asesor").textContent = "";
        }

        $("mi-aviso").classList.remove("oculto");
    }

    if (turno.estado === "atendido") {
        $("mi-detalle").textContent = tramite + ". Tu atención ha finalizado. ¡Gracias por visitarnos!";
        $("btn-nuevo").classList.remove("oculto");
    }

    if (turno.estado === "cancelado") {
        $("mi-detalle").textContent = tramite + ". Este turno fue cancelado.";
        $("btn-nuevo").classList.remove("oculto");
    }
}

$("btn-cancelar").addEventListener("click", async () => {
    if (!confirm("¿Quieres cancelar tu turno?")) return;

    const guardado = leerTurno();
    if (!guardado) return;

    const r = await api("/turnos/" + guardado.id, "PATCH", { estado: "cancelado" });

    mostrarMensaje(r.ok ? "Turno cancelado" : r.datos.mensaje, !r.ok);
    actualizarMiTurno();
    cargarPantalla();
});

$("btn-nuevo").addEventListener("click", () => {
    guardarTurno(null);
    $("ticket").classList.add("vacio");
    $("ticket-codigo").textContent = "—";
    $("ticket-mensaje").textContent = "Cuando pidas un turno, aparecerá aquí.";
    actualizarMiTurno();
    $("solicitar").scrollIntoView();
});

// Recuperar el turno propio escribiendo el documento
$("form-consulta").addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const nota = $("c-nota");
    const documento = $("c-documento").value.trim();

    const rCliente = await api("/clientes?documento=" + encodeURIComponent(documento));

    if (!rCliente.ok) {
        nota.textContent = rCliente.datos.mensaje;
        nota.className = "nota error";
        return;
    }

    if (rCliente.datos.length === 0) {
        nota.textContent = "No encontramos ese documento.";
        nota.className = "nota error";
        return;
    }

    const rTurnos = await api("/turnos?cliente_id=" + rCliente.datos[0].id);

    const activos = rTurnos.ok
        ? rTurnos.datos.filter((t) => t.estado === "en_espera" || t.estado === "en_atencion")
        : [];

    if (activos.length === 0) {
        nota.textContent = "No tienes turnos activos.";
        nota.className = "nota error";
        return;
    }

    activos.sort((a, b) => b.id - a.id);
    guardarTurno({ id: activos[0].id, codigo: activos[0].codigo });

    nota.textContent = "";
    $("form-consulta").reset();
    actualizarMiTurno();
});

// -----------------------------------------------------
// Inicio
// -----------------------------------------------------

function actualizarTodo() {
    cargarPantalla();
    actualizarMiTurno();
}

actualizarTodo();
setInterval(actualizarTodo, 4000);
