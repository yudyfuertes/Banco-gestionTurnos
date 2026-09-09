# Servicio: Turnos

## Responsabilidad

Genera el número de turno, define la cola por tipo de servicio y prioridad.

## ¿Qué información manejará?

- Tipo de trámite y prioridad

## ¿Con qué otros servicios se comunicará?

- Clientes: para identificar al cliente y asociar sus datos al turno.
- Asesores: para saber qué ventanilla está disponible y asignar el turno.

## Endpoints propuestos

Método: POST
Ruta: "/turnos" 
Descripción general del funcionamiento: Recibe los datos del trámite, consulta a Clientes y genera el turno

Método: POST
Ruta: "/turnos/{id_turno}" 
Descripción general del funcionamiento: Consulta el estado actual de un turno específico

Método: PUT
Ruta: "/turnos/{id_turno}/atender" 
Descripción general del funcionamiento: Marca un turno como "atendiendo" y le asigna una ventanilla

## Estado actual

- Definir la posible comunicación HTTP con el servicio de clientes y asesores