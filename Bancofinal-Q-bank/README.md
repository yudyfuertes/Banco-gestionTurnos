# Q-Bank — Gestión de turnos bancarios

Sistema distribuido (microservicios) para digitalizar la atención presencial en un banco: el cliente toma un turno, el sistema lo registra, el asesor lo llama desde su ventanilla y el cliente recibe el aviso.

**Integrantes:** Elizabeth Pinto Rebolledo, Alix Fernanda Collazos Sarria, Valeria Sanchez Pizo, Yudy Alexandra Fuertes Cuasapud.

## Arquitectura

```
Cliente → Home (8080) → Gateway (5000) → Clientes | Asesores | Turnos | Notificaciones
 mysql_clientes
mysql_asesores
mysql_turnos
mysql_notificaciones
```

Comunicación entre servicios (HTTP, con Timeout y Circuit Breaker):

```
Clientes       → Turnos           pide crear un turno
Turnos         → Clientes         valida y consulta al cliente
Turnos         → Asesores         consulta al asesor
Asesores       → Turnos           atiende y finaliza el turno
Asesores       → Notificaciones   avisa al cliente
Notificaciones → Turnos           consulta cliente y ventanilla
```

Diagramas anteriores en `docs/arquitectura/`.

## Microservicios


| Clientes | Registrar y administrar clientes | `clientes_db` | Terminado |
| Asesores | Administrar asesores y ventanillas; atender y finalizar turnos | `asesores_db` | Terminado |
| Turnos | Crear turnos y controlar su estado | 
`turnos_db` | Terminado |
| Notificaciones | Avisar al cliente cuando se llama su turno | 
`notificaciones_db` | Terminado |
| Gateway | Punto de entrada único, reenvía a los servicios  | Terminado |
| Home | Página web para los clientes | Terminado |

Cada servicio corre en su propio contenedor (Flask, puerto 5000 interno) y solo accede a su propia base de datos.

## Endpoints

Todos funcionan directo (puertos 5001 a 5004) o por el gateway (`http://localhost:5000`).

**CRUD** `clientes`, `asesores`, `turnos`, `notificaciones`):

| Método | Ruta | Función | Respuestas |
|---|---|---|---|
| GET | `/{recurso}` | Listar | 200 |
| GET | `/{recurso}/{id}` | Consultar uno | 200, 404 |
| POST | `/{recurso}` | Crear | 201, 400 (faltan datos), 409 (repetido) |
| PUT | `/{recurso}/{id}` | Actualizar todos los campos | 200, 400, 404 |
| PATCH | `/{recurso}/{id}` | Actualizar algunos campos | 200, 404 |
| DELETE | `/{recurso}/{id}` | Eliminar | 200, 404 |

**Operaciones propias:**

| Método | Ruta | Función |
|---|---|---|
| POST | `/clientes/{id}/solicitar-turno` | Pide a Turnos un turno para el cliente (`tramite`) |
| PUT | `/asesores/{id}/atender-turno/{turno_id}` | El asesor llama el turno y se genera la notificación |
| PUT | `/asesores/{id}/finalizar-turno/{turno_id}` | El asesor termina la atención |
| GET | `/turnos/{id}/detalle` | Turno con datos del cliente y del asesor |
| GET | `/{servicio}/circuito/{destino}` | Estado del Circuit Breaker (`CLOSED`, `OPEN`, `HALF-OPEN`) |

Campos obligatorios al crear: clientes `nombre` y `documento`; asesores `nombre` y `ventanilla`; turnos `cliente_id`; notificaciones `turno_id`.

**Errores:** 400 datos incompletos, 404 no existe, 409 repetido o conflicto, 502 error del servicio llamado, 503 servicio caído , 504 tiempo de espera agotado.

## Bases de datos y persistencia

Un contenedor MySQL por servicio, cada uno con su base, su contraseña y su volumen de Docker:

| Servicio | Contenedor | Base | Volumen | Puerto en el equipo |
|---|---|---|---|---|
| Clientes | `mysql_clientes` | `clientes_db` | `clientes_data` | 3307 |
| Asesores | `mysql_asesores` | `asesores_db` | `asesores_data` | 3308 |
| Turnos | `mysql_turnos` | `turnos_db` | `turnos_data` | 3309 |
| Notificaciones | `mysql_notificaciones` | `notificaciones_db` | `notificaciones_data` | 3310 |

Las tablas y los datos de ejemplo se crean la primera vez desde `bases_datos/*.sql`. Los datos se conservan mientras no se borren los volúmenes.

## Timeout y Circuit Breaker

- **Timeout:** toda llamada entre servicios espera como máximo 2 segundos (`*_TIMEOUT` en el `.env`). Si se pasa, responde 504.
- **Circuit Breaker** (`pybreaker`): tras 3 fallos seguidos (`CB_MAX_FALLOS`) el circuito se abre y responde 503 de inmediato; a los 30 segundos (`CB_RECUPERACION`) prueba de nuevo y si el servicio responde, se cierra.

| Servicio que llama | Servicio protegido | Consultar estado |
|---|---|---|
| Turnos | Clientes | `GET /turnos/circuito/clientes` |
| Turnos | Asesores | `GET /turnos/circuito/asesores` |
| Clientes | Turnos | `GET /clientes/circuito/turnos` |
| Asesores | Turnos | `GET /asesores/circuito/turnos` |
| Asesores | Notificaciones | `GET /asesores/circuito notificaciones` |
| Notificaciones | Turnos | `GET /notificaciones/circuito/turnos` |

**Prueba de fallo y recuperación** (sin borrar volúmenes):

```
docker compose stop clientes        # Turnos no puede consultar a Clientes
POST /turnos  (3 veces)             # el circuito se abre
GET  /turnos/circuito/clientes      # OPEN
docker compose start clientes
# esperar 30 segundos
POST /turnos                        # 201, el circuito vuelve a CLOSED
```

Para probar el Timeout: `docker compose pause turnos`, hacer una petición que lo necesite (responde 504) y `docker compose unpause turnos`.

## API Gateway

El gateway (`gateway/`) recibe todas las peticiones y las reenvía al servicio según la ruta, con el mismo método y cuerpo:

| Ruta | Servicio |
|---|---|
| `/clientes...` | Clientes |
| `/asesores...` | Asesores |
| `/turnos...` | Turnos |
| `/notificaciones...` | Notificaciones |

Si el servicio no responde en 5 segundos devuelve 504; si no se puede conectar, 503.

## Home

Página web (HTML, CSS y JS con Nginx) que solo se comunica con el gateway: ver turnos en pantalla, pedir un turno con el documento y consultar el estado del turno propio. Las acciones del asesor (llamar y finalizar turno) se hacen con Thunder Client o Postman por el gateway.


## Configuración (`.env`)

Un solo `.env` en la raíz. Se define por servicio: `<SERVICIO>_DB_HOST`, `_DB_NAME`, `_DB_PASSWORD` y `_MYSQL_HOST_PORT`. Comunes: `DB_PORT=3306`, `DB_USER=root`, las URLs de los servicios, los timeouts y `CB_MAX_FALLOS` / `CB_RECUPERACION`. El compose entrega a cada servicio sus variables `DB_*`.

## Pruebas

| Prueba | Resultado esperado | Resultado obtenido |
|---|---|---|
| Docker Compose | Todos los contenedores en `Up` | Pendiente |
| CRUD de cada servicio | POST, GET, PUT, DELETE y 404 correctos | Pendiente |
| Persistencia | Los datos siguen tras recrear los contenedores | Pendiente |
| Comunicación HTTP | Crear un turno consulta al cliente | Pendiente |
| Timeout | 504 con el servicio en pausa | Pendiente |
| Circuit Breaker | CLOSED → OPEN → HALF-OPEN → CLOSED | Pendiente |
| Gateway | Acceso a los 4 servicios | Pendiente |
| Home | Pedir un turno desde la página | Pendiente |

## Estado actual

**Terminado:** los 4 servicios con CRUD, bases independientes con volumen, comunicación HTTP, Timeout, Circuit Breaker, gateway, home y Docker Compose.




