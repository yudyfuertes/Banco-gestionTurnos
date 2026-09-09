# Servicio: Notificaciones

## Responsabilidad

Informa al cliente cuándo su turno va a ser atendido y en qué ventanilla será atendido.

## ¿Qué información maneja?

- Código del turno 
- Ventanilla asignada

## ¿Con qué otros servicios se comunica?

Turnos: para saber qué turno debe notificar, cuándo será atendido y en qué ventanilla.

## Endpoints

Método: POST
Ruta: "/notificaciones" 
Descripción general del funcionamiento: Generar una notificación para un turno y ventanilla específicos, consultando previamente a Turnos 

Método: GET
Ruta: "/notificaciones" 
Descripción general del funcionamiento: Lista todas las notificaciones generadas 

## Estado de la primera entrega (avance general)

- Definir la posible comunicación HTTP con el servicio Turnos 
