# Servicio: Clientes

## Responsabilidad

Registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite).

## ¿Qué información manejará?

- Información del cliente: nombre, tipo de documento, número de documento, celular, tipo de trámite.

## ¿Con qué otros servicios se comunicará?

Clientes no inicia comunicación con otros servicios; responde a las solicitudes que le llegan desde Turnos, quien lo consulta para identificar al cliente y asociar sus datos al turno generado.

## Endpoints propuestos

Método: POST
Ruta: "/clientes" 
Descripción general del funcionamiento: Registra un cliente nuevo o devuelve el existente si el número de documento ya está registrado 

Método: GET
Ruta: "/clientes/{id_cliente}" 
Descripción general del funcionamiento: Consulta los datos de un cliente por su id

## Estado de la primera entrega (avance general)

- Diseñado 