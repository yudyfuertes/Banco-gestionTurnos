// =====================================================
// Q-Bank - Frontend
// El navegador llama a /api/... y nginx reenvía la
// petición al servicio correspondiente (clientes, asesores, turnos).
// =====================================================

const nombresEstado = {
    en_espera: "En espera",
    en_atencion: "En atención",
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

let clientes = [];
let asesores = [];
let turnos = [];

// -----------------------------------------------------
// Trámites que atiende cada asesor
// Se guarda solo en el navegador (los servicios no se tocan).
// Un asesor sin configuración atiende todos los trámites.
// -----------------------------------------------------

const CLAVE_TRAMITES = "qbank_tramites_por_asesor";

function leerConfigTramites() {
    try {
        return JSON.parse(localStorage.getItem(CLAVE_TRAMITES)) || {};
    } catch (error) {
        return {};
    }
}

function guardarConfigTramites(config) {
    try {
        localStorage.setItem(CLAVE_TRAMITES, JSON.stringify(config));
    } catch (error) {
        mostrarMensaje("No se pudo guardar la configuración en este navegador", true);
    }
}

function tramitesDe(asesor) {
    const valor = leerConfigTramites()[asesor.id];
    if (Array.isArray(valor)) return valor;
    if (typeof valor === "string") return [valor];
    return [];   // todavía no tiene trámite asignado
}

function atiende(asesor, tramite) {
    return tramitesDe(asesor).includes(tramite);
}

function cargaDe(asesor) {
    return turnos.filter((t) =>
        t.asesor_id === asesor.id && (t.estado === "en_espera" || t.estado === "en_atencion")
    ).length;
}

// Elige entre los asesores del trámite al que tenga menos turnos pendientes
function elegirAsesor(tramite) {
    const candidatos = asesores.filter((a) => atiende(a, tramite));
    if (candidatos.length === 0) return null;

    return candidatos.sort((a, b) => cargaDe(a) - cargaDe(b) || a.id - b.id)[0];
}

// Turnos en espera de un asesor, en orden de llegada
// (incluye turnos antiguos sin asesor que correspondan a sus trámites)
function colaDe(asesor) {
    return turnosEnEspera().filter((t) =>
        t.asesor_id === asesor.id ||
        (t.asesor_id === null && t.asesor_id !== undefined && atiende(asesor, t.tramite))
    );
}

// -----------------------------------------------------
// Utilidades
// -----------------------------------------------------

function $(id) {
    return document.getElementById(id);
}

function esc(texto) {
    const div = document.createElement("div");
    div.textContent = texto === null || texto === undefined ? "" : texto;
    return div.innerHTML;
}

async function api(ruta, metodo = "GET", cuerpo = null) {
    const opciones = { method: metodo, headers: {} };

    if (cuerpo) {
        opciones.headers["Content-Type"] = "application/json";
        opciones.body = JSON.stringify(cuerpo);
    }

    let respuesta;
    try {
        respuesta = await fetch("/api" + ruta, opciones);
    } catch (error) {
        return { ok: false, status: 0, datos: { mensaje: "No hay conexión con el servidor" } };
    }

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

// -----------------------------------------------------
// Carga de datos
// -----------------------------------------------------

async function cargarTodo() {
    const [rClientes, rAsesores, rTurnos] = await Promise.all([
        api("/clientes"),
        api("/asesores"),
        api("/turnos")
    ]);

    if (rClientes.ok) clientes = rClientes.datos;
    if (rAsesores.ok) asesores = rAsesores.datos;
    if (rTurnos.ok) turnos = rTurnos.datos;

    ponerServicio("svc-clientes", rClientes.ok);
    ponerServicio("svc-asesores", rAsesores.ok);
    ponerServicio("svc-turnos", rTurnos.ok);

    dibujarInicio();
    dibujarTurnos();
    dibujarAsesores();
    actualizarTramitesDisponibles();
    dibujarClientes();
    cargarCircuitos();
}

function ponerServicio(id, activo) {
    const pill = $(id);
    pill.textContent = activo ? "Activo" : "Caído";
    pill.className = "pill " + (activo ? "verde" : "rojo");
}

async function cargarCircuitos() {
    const lista = [
        ["cb-turnos-clientes", "/turnos/circuito/clientes"],
        ["cb-turnos-asesores", "/turnos/circuito/asesores"],
        ["cb-clientes-turnos", "/clientes/circuito/turnos"],
        ["cb-asesores-turnos", "/asesores/circuito/turnos"]
    ];

    for (const [id, ruta] of lista) {
        const r = await api(ruta);
        const pill = $(id);

        if (!r.ok) {
            pill.textContent = "Sin respuesta";
            pill.className = "pill";
            continue;
        }

        const estado = r.datos.estado;
        pill.textContent = estado;

        if (estado === "CLOSED") pill.className = "pill verde";
        else if (estado === "OPEN") pill.className = "pill rojo";
        else pill.className = "pill amarillo";
    }
}

// -----------------------------------------------------
// Búsquedas auxiliares
// -----------------------------------------------------

function buscarCliente(id) {
    return clientes.find((c) => c.id === id);
}

function buscarAsesor(id) {
    return asesores.find((a) => a.id === id);
}

// Turno que el cliente todavía tiene pendiente (en espera o en atención)
function turnoActivoDe(clienteId) {
    return turnos.find((t) =>
        t.cliente_id === clienteId && (t.estado === "en_espera" || t.estado === "en_atencion")
    );
}

function turnosEnEspera() {
    return turnos
        .filter((t) => t.estado === "en_espera")
        .sort((a, b) => a.id - b.id);
}

// -----------------------------------------------------
// Inicio
// -----------------------------------------------------

function dibujarInicio() {
    $("stat-espera").textContent = turnos.filter((t) => t.estado === "en_espera").length;
    $("stat-atencion").textContent = turnos.filter((t) => t.estado === "en_atencion").length;
    $("stat-atendidos").textContent = turnos.filter((t) => t.estado === "atendido").length;

    const enAtencion = turnos
        .filter((t) => t.estado === "en_atencion")
        .sort((a, b) => b.id - a.id);

    const estado = $("hero-estado");

    if (enAtencion.length === 0) {
        estado.textContent = "● Sin turnos en atención";
        estado.className = "status inactivo";
        $("hero-codigo").textContent = "—";
        $("hero-tramite").textContent = "—";
        $("hero-ventanilla").textContent = "—";
        $("hero-asesor").textContent = "—";
        return;
    }

    const turno = enAtencion[0];
    const asesor = buscarAsesor(turno.asesor_id);

    estado.textContent = "● En atención";
    estado.className = "status";
    $("hero-codigo").textContent = turno.codigo;
    $("hero-tramite").textContent = nombresTramite[turno.tramite] || turno.tramite;
    $("hero-ventanilla").textContent = asesor ? String(asesor.ventanilla).padStart(2, "0") : "—";
    $("hero-asesor").textContent = asesor ? asesor.nombre : "—";
}

// -----------------------------------------------------
// Solicitar turno
// -----------------------------------------------------

$("t-documento").addEventListener("input", () => {
    const documento = $("t-documento").value.trim();
    const cliente = clientes.find((c) => c.documento === documento);
    const nota = $("t-nota");

    if (cliente) {
        $("t-nombre").value = cliente.nombre;
        $("t-telefono").value = cliente.telefono || "";
        const activo = turnoActivoDe(cliente.id);
        if (activo) {
            nota.textContent = "Este documento ya tiene el turno " + activo.codigo + " activo.";
            nota.className = "nota error";
        } else {
            nota.textContent = "Cliente registrado: " + cliente.nombre;
            nota.className = "nota ok";
        }
    } else {
        nota.textContent = "";
        nota.className = "nota";
    }
});

$("form-turno").addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const boton = $("t-boton");
    const nota = $("t-nota");
    const documento = $("t-documento").value.trim();
    const nombre = $("t-nombre").value.trim();
    const telefono = $("t-telefono").value.trim();
    const tramite = $("t-tramite").value;

    boton.disabled = true;
    boton.textContent = "Solicitando...";
    nota.textContent = "";

    // 1. Buscar el cliente por documento (o registrarlo si es nuevo)
    const rLista = await api("/clientes");
    if (!rLista.ok) {
        terminarSolicitud(rLista.datos.mensaje, true);
        return;
    }

    let cliente = rLista.datos.find((c) => c.documento === documento);
    let clienteId;

    if (cliente) {
        clienteId = cliente.id;

        // Un mismo documento no puede tener dos turnos activos a la vez
        const rActual = await api("/turnos");
        if (rActual.ok) turnos = rActual.datos;
        const activo = turnoActivoDe(cliente.id);
        if (activo) {
            terminarSolicitud(
                "El documento " + documento + " ya tiene un turno activo (" + activo.codigo +
                "). Debe esperar su llamado antes de pedir otro.", true);
            return;
        }
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

    // 2. Elegir el asesor que atiende este trámite
    const rA = await api("/asesores");
    const rT = await api("/turnos");
    if (rA.ok) asesores = rA.datos;
    if (rT.ok) turnos = rT.datos;

    const asesorAsignado = elegirAsesor(tramite);
    if (!asesorAsignado) {
        terminarSolicitud("Trámite no disponible: por ahora no hay un asesor que atienda «" +
            (nombresTramite[tramite] || tramite) + "».", true);
        return;
    }

    // 3. Clientes le pide a Turnos que cree el turno
    const rTurno = await api("/clientes/" + clienteId + "/solicitar-turno", "POST", {
        tramite: tramite
    });

    if (!rTurno.ok) {
        terminarSolicitud(rTurno.datos.mensaje, true);
        return;
    }

    // 4. Dejar el turno asignado de una vez al asesor (el estado sigue en espera)
    const rAsignar = await api("/turnos/" + rTurno.datos.id, "PATCH", {
        asesor_id: asesorAsignado.id
    });

    await cargarTodo();

    const delAsesor = turnosEnEspera().filter((t) => t.asesor_id === asesorAsignado.id);
    const posicion = delAsesor.findIndex((t) => t.id === rTurno.datos.id) + 1;

    const ticket = $("ticket");
    ticket.classList.remove("vacio");
    $("ticket-codigo").textContent = rTurno.datos.codigo;
    $("ticket-mensaje").innerHTML = rAsignar.ok
        ? "Te atiende <strong>" + esc(asesorAsignado.nombre) + "</strong> en la ventanilla <strong>" +
          esc(asesorAsignado.ventanilla) + "</strong>.<br>" +
          (posicion > 1
              ? "Hay " + (posicion - 1) + " turno(s) antes que el tuyo."
              : "Eres el siguiente en su fila.")
        : "Turno creado, pero no se pudo asignar asesor. Espera tu llamado.";

    $("form-turno").reset();
    terminarSolicitud("Turno " + rTurno.datos.codigo + " creado", false);
});

// Marca como "no disponible" los trámites que ningún asesor atiende todavía
function actualizarTramitesDisponibles() {
    const select = $("t-tramite");
    let hayDisponible = false;

    for (const opcion of select.options) {
        const disponible = asesores.some((a) => atiende(a, opcion.value));
        opcion.disabled = !disponible;
        opcion.textContent = (nombresTramite[opcion.value] || opcion.value) +
            (disponible ? "" : " — no disponible");
        if (disponible) hayDisponible = true;
    }

    // Si el trámite elegido dejó de estar disponible, pasar al primero que sí lo esté
    if (select.selectedOptions[0] && select.selectedOptions[0].disabled) {
        const libre = Array.from(select.options).find((o) => !o.disabled);
        if (libre) select.value = libre.value;
    }

    $("t-boton").disabled = !hayDisponible;

    const aviso = $("t-aviso");
    aviso.textContent = hayDisponible
        ? ""
        : "Por ahora no hay asesores con trámite asignado. Asigna uno en el panel de asesores.";
}

function terminarSolicitud(mensaje, esError) {
    const boton = $("t-boton");
    boton.textContent = "Pedir turno";
    actualizarTramitesDisponibles();

    const nota = $("t-nota");
    nota.textContent = mensaje;
    nota.className = "nota " + (esError ? "error" : "ok");

    mostrarMensaje(mensaje, esError);
}

// -----------------------------------------------------
// Fila de turnos
// -----------------------------------------------------

const gruposTurnos = [
    ["todos", null],
    ["en_espera", "en_espera"],
    ["en_atencion", "en_atencion"],
    ["atendido", "atendido"],
    ["cancelado", "cancelado"]
];

function dibujarTurnos() {
    const enEspera = turnosEnEspera();
    const ordenados = turnos.slice().sort((a, b) => a.id - b.id);

    for (const [clave, estado] of gruposTurnos) {
        const lista = estado ? ordenados.filter((t) => t.estado === estado) : ordenados;
        $("cuenta-" + clave).textContent = lista.length;
        const cuerpo = $("tabla-" + clave);

        if (lista.length === 0) {
            cuerpo.innerHTML = '<tr><td class="vacia" colspan="7">No hay turnos para mostrar</td></tr>';
            continue;
        }

        cuerpo.innerHTML = lista.map((t) => {
            const cliente = buscarCliente(t.cliente_id);
            const asesor = buscarAsesor(t.asesor_id);
            const filaDelAsesor = asesor
                ? enEspera.filter((x) => x.asesor_id === asesor.id)
                : enEspera;
            const posicion = t.estado === "en_espera"
                ? filaDelAsesor.findIndex((x) => x.id === t.id) + 1
                : "—";
            const cancelar = t.estado === "en_espera"
                ? '<button class="mini peligro" data-accion="cancelar" data-id="' + t.id + '">Cancelar</button>'
                : "";

            return "<tr>" +
                '<td class="codigo">' + esc(t.codigo) + "</td>" +
                "<td>" + esc(cliente ? cliente.nombre : "Cliente " + t.cliente_id) + "</td>" +
                "<td>" + esc(nombresTramite[t.tramite] || t.tramite) + "</td>" +
                '<td><span class="etiqueta e-' + esc(t.estado) + '">' + esc(nombresEstado[t.estado] || t.estado) + "</span></td>" +
                "<td>" + posicion + "</td>" +
                "<td>" + (asesor ? "<strong>" + esc(asesor.ventanilla) + "</strong> · " + esc(asesor.nombre) : "Sin asignar") + "</td>" +
                '<td><button class="mini" data-accion="detalle" data-id="' + t.id + '">Detalle</button>' + cancelar + "</td>" +
                "</tr>";
        }).join("");
    }
}

$("filas-turnos").addEventListener("click", async (evento) => {
    const boton = evento.target.closest("button");
    if (!boton) return;

    const id = Number(boton.dataset.id);

    if (boton.dataset.accion === "detalle") {
        verDetalle(id);
    }

    if (boton.dataset.accion === "cancelar") {
        if (!confirm("¿Cancelar este turno?")) return;

        const r = await api("/turnos/" + id, "PATCH", { estado: "cancelado" });
        mostrarMensaje(r.datos.mensaje, !r.ok);
        cargarTodo();
    }
});

// -----------------------------------------------------
// Detalle del turno (Turnos consulta a Clientes y Asesores)
// -----------------------------------------------------

async function verDetalle(id) {
    $("modal-contenido").innerHTML = "<p>Consultando...</p>";
    $("modal").classList.remove("oculto");

    const r = await api("/turnos/" + id + "/detalle");

    if (!r.ok) {
        $("modal-contenido").innerHTML =
            '<p class="nota error">' + esc(r.datos.mensaje) + "</p>";
        return;
    }

    const turno = r.datos.turno;
    const cliente = r.datos.cliente;
    const asesor = r.datos.asesor;

    let html =
        '<div class="modal-grupo"><h4>Turno</h4>' +
        '<p><strong class="codigo">' + esc(turno.codigo) + "</strong> · " +
        esc(nombresTramite[turno.tramite] || turno.tramite) + "</p>" +
        '<p><span class="etiqueta e-' + esc(turno.estado) + '">' +
        esc(nombresEstado[turno.estado] || turno.estado) + "</span></p></div>" +
        '<div class="modal-grupo"><h4>Cliente</h4>' +
        "<p>" + esc(cliente.nombre) + "</p>" +
        "<p>Documento: " + esc(cliente.documento) + "</p>" +
        "<p>Teléfono: " + esc(cliente.telefono || "—") + "</p></div>";

    if (asesor) {
        html += '<div class="modal-grupo"><h4>Asesor</h4>' +
            "<p>" + esc(asesor.nombre) + "</p>" +
            "<p>Ventanilla: " + esc(asesor.ventanilla) + "</p></div>";
    } else {
        html += '<div class="modal-grupo"><h4>Asesor</h4><p>Aún no tiene asesor asignado</p></div>';
    }

    $("modal-contenido").innerHTML = html;
}

$("modal-cerrar").addEventListener("click", () => $("modal").classList.add("oculto"));
$("modal").addEventListener("click", (evento) => {
    if (evento.target === $("modal")) $("modal").classList.add("oculto");
});

// -----------------------------------------------------
// Asesores
// -----------------------------------------------------

function dibujarAsesores() {
    const contenedor = $("lista-asesores");

    if (asesores.length === 0) {
        contenedor.innerHTML = '<p class="nota nota-centro">No hay asesores registrados</p>';
        return;
    }

    contenedor.innerHTML = asesores.map((a) => {
        const turnoActual = turnos.find((t) => t.asesor_id === a.id && t.estado === "en_atencion");
        const ocupado = a.estado === "ocupado";
        const mis = tramitesDe(a);
        const enCola = colaDe(a).length;

        // Trámite: fijo una vez asignado. Si aún no tiene, el administrador lo asigna una sola vez.
        let bloqueTramite;
        if (mis.length > 0) {
            bloqueTramite = '<div class="asesor-tramites"><small>Atiende</small>' +
                mis.map((t) => '<span class="chip activo fijo">' + esc(nombresTramite[t] || t) + "</span>").join(" ") +
                "</div>";
        } else {
            bloqueTramite = '<div class="asesor-tramites"><small>Sin trámite asignado</small>' +
                '<div class="asignar-linea"><select id="sel-' + a.id + '">' +
                Object.keys(nombresTramite).map((k) =>
                    '<option value="' + k + '">' + esc(nombresTramite[k]) + "</option>").join("") +
                '</select><button class="mini" data-accion="asignar" data-id="' + a.id + '">Asignar</button></div></div>';
        }

        const infoTurno = turnoActual
            ? "Atendiendo: <strong>" + esc(turnoActual.codigo) + "</strong>"
            : "Sin turno en atención";

        const sinCola = enCola === 0 ? " disabled" : "";

        return '<article class="asesor-card">' +
            '<div class="asesor-top">' +
            '<div class="ventanilla-num">' + esc(a.ventanilla) + "</div>" +
            "<div><h3>" + esc(a.nombre) + "</h3><small>Ventanilla " + esc(a.ventanilla) + "</small></div>" +
            "</div>" +
            '<p style="margin-bottom:14px"><span class="etiqueta e-' + esc(a.estado) + '">' + esc(a.estado) + "</span></p>" +
            bloqueTramite +
            '<div class="asesor-turno">' + infoTurno + "<br><small>En su fila: <strong>" + enCola + "</strong> turno(s)</small></div>" +
            '<div class="asesor-acciones">' +
            '<button class="mini" data-accion="llamar" data-id="' + a.id + '"' + (ocupado || mis.length === 0 ? " disabled" : sinCola) + ">Llamar siguiente</button>" +
            '<button class="mini" data-accion="finalizar" data-id="' + a.id + '"' + (ocupado ? "" : " disabled") + ">Finalizar atención</button>" +
            '<button class="mini peligro" data-accion="eliminar" data-id="' + a.id + '"' + (ocupado ? " disabled" : "") + ">Eliminar</button>" +
            "</div>" +
            "</article>";
    }).join("");
}

$("lista-asesores").addEventListener("click", async (evento) => {
    const boton = evento.target.closest("button");
    if (!boton) return;

    const id = Number(boton.dataset.id);
    const accion = boton.dataset.accion;

    if (accion === "asignar") {
        const tramite = $("sel-" + id).value;
        const config = leerConfigTramites();
        config[id] = [tramite];
        guardarConfigTramites(config);
        mostrarMensaje("Trámite asignado: " + nombresTramite[tramite]);
    }

    if (accion === "llamar") {
        const asesor = buscarAsesor(id);
        const siguiente = asesor ? colaDe(asesor)[0] : null;

        if (!siguiente) {
            mostrarMensaje("No hay turnos en espera para este asesor", true);
            return;
        }

        const r = await api("/asesores/" + id + "/atender-turno/" + siguiente.id, "PUT");
        mostrarMensaje(
            r.ok ? "Llamando al turno " + siguiente.codigo : r.datos.mensaje,
            !r.ok
        );
    }

    if (accion === "finalizar") {
        const actual = turnos.find((t) => t.asesor_id === id && t.estado === "en_atencion");

        if (!actual) {
            mostrarMensaje("Este asesor no tiene un turno en atención", true);
            return;
        }

        const r = await api("/asesores/" + id + "/finalizar-turno/" + actual.id, "PUT");
        mostrarMensaje(
            r.ok ? "Turno " + actual.codigo + " finalizado" : r.datos.mensaje,
            !r.ok
        );
    }

    if (accion === "eliminar") {
        if (!confirm("¿Eliminar este asesor?")) return;

        const r = await api("/asesores/" + id, "DELETE");
        mostrarMensaje(r.datos.mensaje, !r.ok);
    }

    cargarTodo();
});

$("form-asesor").addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const tramiteNuevo = $("a-tramite").value;
    const ventanillaNueva = Number($("a-ventanilla").value);

    if (asesores.some((a) => a.ventanilla === ventanillaNueva)) {
        mostrarMensaje("La ventanilla " + ventanillaNueva + " ya está ocupada por otro asesor", true);
        return;
    }

    const r = await api("/asesores", "POST", {
        nombre: $("a-nombre").value.trim(),
        ventanilla: Number($("a-ventanilla").value)
    });

    mostrarMensaje(r.datos.mensaje, !r.ok);

    if (r.ok) {
        const config = leerConfigTramites();
        config[r.datos.id] = [tramiteNuevo];
        guardarConfigTramites(config);
        $("form-asesor").reset();
    }
    cargarTodo();
});

// -----------------------------------------------------
// Clientes
// -----------------------------------------------------

$("buscar-cliente").addEventListener("input", dibujarClientes);

function dibujarClientes() {
    const texto = $("buscar-cliente").value.trim().toLowerCase();

    const lista = clientes.filter((c) =>
        c.nombre.toLowerCase().includes(texto) || c.documento.includes(texto)
    );

    const cuerpo = $("tabla-clientes");

    if (lista.length === 0) {
        cuerpo.innerHTML = '<tr><td class="vacia" colspan="4">No hay clientes para mostrar</td></tr>';
        return;
    }

    cuerpo.innerHTML = lista.map((c) =>
        "<tr><td>" + esc(c.id) + "</td><td>" + esc(c.nombre) + "</td><td>" +
        esc(c.documento) + "</td><td>" + esc(c.telefono || "—") + "</td></tr>"
    ).join("");
}

// -----------------------------------------------------
// Inicio de la página
// -----------------------------------------------------

$("ticket").classList.add("vacio");

cargarTodo();
setInterval(cargarTodo, 5000);
