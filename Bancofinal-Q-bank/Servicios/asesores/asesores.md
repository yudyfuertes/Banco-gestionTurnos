# Servicio: Asesores

## Responsabilidad

Gestiona el estado de cada ventanilla (disponible/ocupada) y asigna el turno al asesor.

## ¿Qué información manejará?

- Información de estado de ventanilla (disponible/ocupada).

## ¿Con qué otros servicios se comunicará?

Turnos: para conocer el turno que debe atender y registrar el cierre de la atención.

## Endpoints propuestos


Método: POST
Ruta: "/asesores" 
Descripción general del funcionamiento: Actualiza el estado de una ventanilla (disponible/ocupada)

Método: GET
Ruta: "/asesores/{id_asesores}" 
Descripción general del funcionamiento: Consulta el estado actual de una ventanilla específica

Método: POST
Ruta: "/asesores/atender" 
Descripción general del funcionamiento: Asigna un turno a una ventanilla y notifica a Turnos el cierre de la atención

## Estado de la primera entrega (avance general)

- Definir la posible comunicación HTTP con el servicio Turnos