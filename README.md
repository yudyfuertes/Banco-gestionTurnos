# Banco-gestionTurnos

# Primer avance del proyecto

**Nombre del proyecto:** Q-bank

## Problema que resuelve

Actualmente, la gestión presencial de la atención al cliente en los modelos tradicionales de las entidades bancarias presenta fallas de organización debido a la concurrencia simultánea de usuarios que solicitan diferentes servicios especializados o simples. Esto genera:

- **Filas presenciales abundantes:** Mayor cantidad de usuarios en horas pico sin control de flujo.
- **Tiempos de espera inciertos:** No existen estimaciones en tiempo real para el usuario sobre el estado de su turno.
- **Asignación ineficiente de asesores:** Asesores especializados atendiendo solicitudes simples.
- **Ausencia de priorización:** Falta de priorización en la atención preferencial.

Q-bank es un sistema diseñado para digitalizar y optimizar el flujo de atención presencial. En el momento en que el usuario llega al banco, toma un turno, el sistema lo registra y aplica un ordenamiento según la prioridad de su solicitud. Posteriormente, realiza automáticamente la asignación a una ventanilla disponible y notifica en tiempo real al usuario para indicarle el momento en que debe acercarse para ser atendido.

## Objetivo

Diseñar la estructura inicial de un sistema distribuido para la gestión de turnos bancarios, utilizando una arquitectura basada en microservicios.

## Integrantes

- Elizabeth Pinto Rebolledo
- Alix Fernanda Collazos Sarria
- Valeria Sanchez Pizo
- Yudy Alexandra Fuertes Cuasapud

## Arquitectura del sistema
<img width="719" height="512" alt="Primeravance" src="https://github.com/user-attachments/assets/5cfd9d1f-d972-449b-a3ad-61491e6517cb" />

## Definición de servicios
| Servicio | Responsabilidad | ¿Qué información maneja? | ¿Con qué otros servicios se comunicará? |
|---|---|---|---|
| **Turnos** | Genera el número de turno, define la cola por tipo de servicio y prioridad. | Tipo de trámite y prioridad. | **Clientes:** para identificar al cliente y asociar sus datos al turno.<br>**Asesores:** para saber qué ventanilla está disponible y asignar el turno. |
| **Clientes** | Registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite). | Información del cliente (nombre, tipo de documento, número de documento, celular, tipo de trámite). | **Turnos:** le solicita la creación del turno con los datos del cliente y recibe la confirmación con el número de turno generado. |
| **Asesores** | Gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al asesor. | Información de estado de ventanilla (disponible/ocupada). | **Turnos:** para conocer el turno que debe atender y registrar el cierre de la atención. |
| **Notificaciones** | Informa al cliente cuando su turno va a ser atendido y en qué ventanilla. | Información del estado del turno, y a dónde dirigirse. | **Turnos:** para saber qué turno debe notificar, cuándo será atendido y en qué ventanilla.<br>**Clientes:** llega al cliente la notificación cuando será atendido. |

## Comunicación entre servicios

<img width="718" height="779" alt="Comunicación" src="https://github.com/user-attachments/assets/870f42dd-283d-4f53-a48b-197d3bd4f7e4" />

## Dockerfile vista home
contenedor 
<img width="1260" height="255" alt="image" src="https://github.com/user-attachments/assets/6ed54cc9-1966-4d99-8450-80d35b59c3e1" />
imagen
<img width="1150" height="230" alt="image" src="https://github.com/user-attachments/assets/1601c6b8-fc66-4152-8dcc-aa207390e5a8" />
Home funcionando 
<img width="986" height="487" alt="image" src="https://github.com/user-attachments/assets/6c7b4de7-d074-4c4e-863c-ebcb021cba7e" />

## Docker Compose

El proyecto utiliza Docker Compose para definir y administrar los contenedores correspondientes a los diferentes microservicios del sistema Q-bank.

Actualmente, el archivo `docker-compose.yml` tiene definida la estructura de los cinco servicios principales:

```yaml
services:

  home:
    build: ./home
    ports:
      - "8080:80"

  # clientes-service:
  #   build: ./servicios/clientes
  #   ports:
  #     - "3000:80"

  # turnos-service:
  #   build: ./servicios/turnos
  #   ports:
  #     - "3001:80"
  #   depends_on:
  #     - clientes-service

  # asesores-service:
  #   build: ./servicios/asesores
  #   ports:
  #     - "3002:80"

  # notificaciones-service:
  #   build: ./servicios/notificaciones
  #   ports:
  #     - "3003:80"
  #   depends_on:
  #     - turnos-service
```

### Servicios configurados

| Servicio       | Puerto | Estado       |
| -------------- | -----: | ------------ |
| Home           |   8080 | Implementado |
| Clientes       |   3000 | Pendiente    |
| Turnos         |   3001 | Pendiente    |
| Asesores       |   3002 | Pendiente    |
| Notificaciones |   3003 | Pendiente    |

El servicio Home se encuentra actualmente implementado mediante un `Dockerfile` basado en la imagen `nginx:alpine`.

---

## Estado actual del proyecto

### Diseñado

* Arquitectura completa del sistema.
* Definición de los microservicios.
* Responsabilidades de cada servicio.
* Endpoints propuestos y métodos HTTP.
* Comunicación propuesta entre los diferentes servicios.

### Configurado

* Estructura inicial del archivo `docker-compose.yml`.
* Definición de los cinco servicios principales:

  * Home
  * Clientes
  * Turnos
  * Asesores
  * Notificaciones
* Configuración inicial de puertos.
* Configuración de dependencias entre servicios.

### Implementado

* Vista Home funcionando correctamente dentro de un contenedor Docker.
* `Dockerfile` configurado utilizando la imagen `nginx:alpine`.
* Construcción de la imagen Docker.
* Ejecución del contenedor.
* Acceso al Home mediante el puerto `8080`.

### Pendiente

* Implementación de la lógica de negocio del servicio Clientes.
* Implementación de la lógica de negocio del servicio Turnos.
* Implementación de la lógica de negocio del servicio Asesores.
* Implementación de la lógica de negocio del servicio Notificaciones.
* Implementación de las bases de datos:

  * `clientes-db`
  * `turnos-db`
  * `asesores-db`
  * `notificaciones-db`
* Implementación de la comunicación HTTP entre los microservicios.
* Integración completa de los servicios mediante Docker Compose.

---

## Pull Request
### Resumen

En este avance se establece la estructura inicial del sistema distribuido Q-bank, definiendo la arquitectura basada en microservicios y configurando la infraestructura inicial mediante Docker.

Se implementó y puso en funcionamiento el servicio Home, mientras que los demás microservicios se encuentran definidos en `docker-compose.yml` y serán desarrollados en las siguientes etapas.

# IMPLEMENTACIÓN DE SERVICIOS

Se implementaron tres servicios independientes para el sistema Q-Bank. Cada servicio es una aplicación Flask con su propio archivo `app.py`, su `Dockerfile` y su archivo `requirements.txt`. Además, cada servicio se ejecuta en un contenedor independiente.

### 1. Distribución de los servicios

| Servicio | Responsabilidad | Datos administrados |
|---|---|---|
| Clientes | Gestionar los clientes del banco. | Nombre, documento de identidad y teléfono. |
| Asesores | Gestionar los asesores y sus ventanillas de atención. | Nombre, ventanilla y estado del asesor. |
| Turnos | Gestionar los turnos de atención. | Código del turno, cliente, asesor, trámite, estado y fecha de creación. |

### 2. Cumplimiento de los requisitos

| Requisito | Cómo se cumple en Q-Bank |
|---|---|
| Tener una responsabilidad específica | Cada servicio gestiona una única entidad: clientes, asesores o turnos. Ningún servicio accede directamente a las tablas de otro. |
| Administrar información propia | Cada servicio lee y escribe únicamente en su propia base de datos. Turnos almacena `cliente_id` y `asesor_id` y obtiene los datos completos mediante solicitudes REST. |
| Exponer una API REST | Los tres servicios utilizan Flask y devuelven respuestas en formato JSON mediante los métodos GET, POST, PUT y DELETE, utilizando códigos HTTP como 200, 201, 400, 404, 409 y 503. |
| Tener persistencia de datos | Cada servicio almacena su información en MySQL 8.0, utilizando un volumen de Docker para persistir los datos de su base de datos. |
| Poder ejecutarse independientemente | Cada servicio cuenta con su propio Dockerfile, contenedor y puerto (5001, 5002 y 5003). Si Clientes o Asesores se detienen, Turnos puede atender las consultas que no dependan de ellos y responde con el código 503 cuando necesita comunicarse con un servicio que no está disponible. |

---

# DISEÑO DE RESPONSABILIDADES

Se definieron las responsabilidades de cada servicio, la información que administra y la forma en que se comunica con los demás servicios del sistema Q-Bank.

### 1. Responsabilidades y comunicación entre servicios

| Servicio | Responsabilidad | Información administrada | Comunicación con otros servicios |
|---|---|---|---|
| Clientes | Registrar, consultar, actualizar y eliminar clientes del banco. | `id`, nombre, documento único y teléfono. | No consulta otros servicios. Es consultado por Turnos mediante `GET /clientes/{id}`. |
| Asesores | Registrar, consultar, actualizar y eliminar asesores y sus ventanillas. | `id`, nombre, ventanilla y estado (por defecto, disponible). | No consulta otros servicios. Es consultado por Turnos mediante `GET /asesores/{id}`. |
| Turnos | Crear turnos, asignarles un asesor y controlar su estado. | `id`, código (T-001), `cliente_id`, `asesor_id`, trámite, estado y fecha de creación. | Se comunica mediante REST con Clientes y Asesores para validar su existencia y obtener la información necesaria para mostrar el detalle del

## IMPLEMENTACION DE APIS REST

Cada servicio implementa los métodos HTTP principales sobre su recurso. Los datos se envían y se reciben en formato JSON.

| Método | Función | Clientes | Asesores | Turnos |
|--------|---------|----------|----------|--------|
| GET | Consultar información | `/clientes` | `/asesores` | `/turnos` |
| GET/{id} | Consultar un elemento específico | `/clientes/{id}` | `/asesores/{id}` | `/turnos/{id}` |
| POST | Crear información | `/clientes` | `/asesores` | `/turnos` |
| PUT | Actualizar información | `/clientes/{id}` | `/asesores/{id}` | `/turnos/{id}` |
| DELETE | Eliminar información | `/clientes/{id}` | `/asesores/{id}` | `/turnos/{id}` |

Además, el servicio de Turnos expone `GET /turnos/{id}/detalle`, que combina los datos del turno con el nombre del cliente y del asesor.

---

## DOCUMENTACION DE ENDPOINTS

Todos los errores se devuelven en formato JSON con la forma `{"error": "mensaje"}`. Las eliminaciones exitosas devuelven `{"mensaje": "... eliminado"}`.

### Servicio Clientes (puerto 5001)

| Método | Endpoint | Descripción | Entrada | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/clientes` | Consultar clientes | Ninguna | 200: lista de clientes |
| GET | `/clientes/{id}` | Consultar un cliente | ID del cliente en la ruta | 200: cliente. 404: no encontrado |
| POST | `/clientes` | Crear cliente | JSON: `nombre` y `documento` (obligatorios), `telefono` (opcional) | 201: cliente creado. 400: faltan datos. 409: documento repetido |
| PUT | `/clientes/{id}` | Actualizar cliente | JSON con los campos a modificar | 200: cliente modificado. 404: no encontrado. 409: documento repetido |
| DELETE | `/clientes/{id}` | Eliminar cliente | ID del cliente en la ruta | 200: confirmación. 404: no encontrado |

### Servicio Asesores (puerto 5002)

| Método | Endpoint | Descripción | Entrada | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/asesores` | Consultar asesores | Ninguna | 200: lista de asesores |
| GET | `/asesores/{id}` | Consultar un asesor | ID del asesor en la ruta | 200: asesor. 404: no encontrado |
| POST | `/asesores` | Crear asesor | JSON: `nombre` y `ventanilla` (obligatorios), `estado` (opcional) | 201: asesor creado. 400: faltan datos |
| PUT | `/asesores/{id}` | Actualizar asesor | JSON con los campos a modificar | 200: asesor modificado. 404: no encontrado |
| DELETE | `/asesores/{id}` | Eliminar asesor | ID del asesor en la ruta | 200: confirmación. 404: no encontrado |

### Servicio Turnos (puerto 5003)

| Método | Endpoint | Descripción | Entrada | Respuesta |
|--------|----------|-------------|---------|-----------|
| GET | `/turnos` | Consultar turnos | Ninguna | 200: lista de turnos |
| GET | `/turnos/{id}` | Consultar un turno | ID del turno en la ruta | 200: turno. 404: no encontrado |
| POST | `/turnos` | Crear turno | JSON: `cliente_id` (obligatorio), `asesor_id` y `tramite` (opcionales) | 201: turno con código T-001, T-002… 400: falta `cliente_id`. 404: cliente o asesor inexistente. 503: servicio no disponible |
| PUT | `/turnos/{id}` | Actualizar turno | JSON: `estado`, `asesor_id` y/o `tramite` | 200: turno modificado. 400: estado inválido. 404: no encontrado. 503: servicio no disponible |
| DELETE | `/turnos/{id}` | Eliminar turno | ID del turno en la ruta | 200: confirmación. 404: no encontrado |
| GET | `/turnos/{id}/detalle` | Consultar el turno con el nombre del cliente y del asesor | ID del turno en la ruta | 200: detalle del turno. 404: no encontrado. 503: servicio no disponible |

##  Persistencia de datos

Cada servicio maneja sus propios datos y ninguno los guarda en listas o variables dentro del código: toda la información se almacena en una base de datos MySQL. Los servicios usan el conector `mysql-connector-python`. Por ejemplo, así se inserta un cliente en el servicio Clientes:

**Tabla 8. Aspectos de la persistencia de datos.**

| Aspecto | Implementación |
|---|---|
| Motor de base de datos | MySQL 8.0 (imagen oficial `mysql:8.0`), un contenedor por servicio. |
| Acceso desde el código | Funciones `consultar()` y `ejecutar()` de cada `app.py`, con consultas parametrizadas. |
| Creación de las tablas | Se crean por consola con los comandos `CREATE TABLE` del archivo `INSERTAR_DATOS.md`; los servicios no crean tablas por su cuenta. |
| Datos de ejemplo | Se insertan por consola con los comandos `INSERT` del mismo archivo (2 clientes, 2 asesores y 2 turnos). |
| Conservación de los datos | Cada base usa un volumen de Docker (`clientes_data`, `asesores_data`, `turnos_data`). |
| Espera de la base de datos | Al iniciar, cada servicio reintenta la conexión cada 3 segundos hasta que su base de datos existe. |

---

##  Base de datos por servicio

Cada servicio cuenta con almacenamiento independiente: un contenedor MySQL, una base de datos y un volumen propios.

| Servicio | Base de datos utilizada | Tablas principales | Puerto del contenedor MySQL |
|---|---|---|---|
| Clientes | bd: `clientes_db`<br>Contenedor: `mysql_clientes`<br>Volumen: `clientes_data` | `clientes` | `3307` |
| Asesores | bd: `asesores_db`<br>Contenedor: `mysql_asesores`<br>Volumen: `asesores_data` | `asesores` | `3308` |
| Turnos | bd: `turnos_db`<br>Contenedor: `mysql_turnos`<br>Volumen: `turnos_data` | `turnos` | `3309` |

### Estructura de cada tabla

#### `clientes_db`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | `INT` | Llave primaria, `AUTO_INCREMENT` |
| `nombre` | `VARCHAR(100)` | `NOT NULL` |
| `documento` | `VARCHAR(20)` | `NOT NULL`, `UNIQUE` |
| `telefono` | `VARCHAR(20)` | Opcional |

#### `asesores_db`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | `INT` | Llave primaria, `AUTO_INCREMENT` |
| `nombre` | `VARCHAR(100)` | `NOT NULL` |
| `ventanilla` | `INT` | `NOT NULL` |
| `estado` | `VARCHAR(20)` | `NOT NULL`, valor por defecto `'disponible'` |

#### `turnos_db`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | `INT` | Llave primaria, `AUTO_INCREMENT` |
| `codigo` | `VARCHAR(10)` | Código del turno (T-001, T-002…), generado por el servicio |
| `cliente_id` | `INT` | `NOT NULL`. Referencia lógica a `clientes.id` |
| `asesor_id` | `INT` | Opcional. Referencia lógica a `asesores.id` |
| `tramite` | `VARCHAR(50)` | `NOT NULL`, valor por defecto `'general'` |
| `estado` | `VARCHAR(20)` | `NOT NULL`, valor por defecto `'en_espera'` |
| `creado` | `TIMESTAMP` | Valor por defecto `CURRENT_TIMESTAMP` |

## CONFIGURACIÓN DE LAS VARIABLES DE ENTORNO 
| Variable | Uso |
|---|---|
| `CLIENTES_DB_NAME` | Nombre de la base de datos de clientes. |
| `CLIENTES_DB_USER` | Usuario de MySQL para acceder a la base de datos de clientes. |
| `CLIENTES_DB_PASSWORD` | Contraseña del usuario de MySQL de clientes. |
| `CLIENTES_DB_ROOT_PASSWORD` | Contraseña del usuario root de MySQL de clientes. |
| `CLIENTES_PORT` | Puerto donde se ejecuta el servicio Flask de clientes. |
| `CLIENTES_MYSQL_HOST_PORT` | Puerto del equipo anfitrión utilizado para acceder al MySQL de clientes. |
| `ASESORES_DB_NAME` | Nombre de la base de datos de asesores. |
| `ASESORES_DB_USER` | Usuario de MySQL para acceder a la base de datos de asesores. |
| `ASESORES_DB_PASSWORD` | Contraseña del usuario de MySQL de asesores. |
| `ASESORES_DB_ROOT_PASSWORD` | Contraseña del usuario root de MySQL de asesores. |
| `ASESORES_PORT` | Puerto donde se ejecuta el servicio Flask de asesores. |
| `ASESORES_MYSQL_HOST_PORT` | Puerto del equipo anfitrión utilizado para acceder al MySQL de asesores. |
| `TURNOS_DB_NAME` | Nombre de la base de datos de turnos. |
| `TURNOS_DB_USER` | Usuario de MySQL para acceder a la base de datos de turnos. |
| `TURNOS_DB_PASSWORD` | Contraseña del usuario de MySQL de turnos. |
| `TURNOS_DB_ROOT_PASSWORD` | Contraseña del usuario root de MySQL de turnos. |
| `TURNOS_PORT` | Puerto donde se ejecuta el servicio Flask de turnos. |
| `TURNOS_MYSQL_HOST_PORT` | Puerto del equipo anfitrión utilizado para acceder al MySQL de turnos. |
| `CLIENTES_URL` | URL interna que utiliza Docker para comunicarse con el servicio de clientes. |
| `ASESORES_URL` | URL interna que utiliza Docker para comunicarse con el servicio de asesores. |

## COMUNICACIÓN ENTRE SERVICIOS 
Clientes -> Turnos
 <img width="940" height="323" alt="imagen" src="https://github.com/user-attachments/assets/c205e45c-60e8-4296-a887-4970a649f163" />

La comunicación de turnos y cliente se puede verificar al momento de crear un turno, es necesario que este enlazado a un cliente, por eso, tenemos:
 <img width="940" height="292" alt="imagen" src="https://github.com/user-attachments/assets/01fab791-6eb9-4a01-a6aa-6492db631fe5" />

Turnos -> asesores
Si el servicio de asesores no esta disponible, este lanza una respuesta de error
 <img width="940" height="300" alt="imagen" src="https://github.com/user-attachments/assets/27490c63-f894-4e75-afa4-f46481a39be4" />

turnos -> asesor
 <img width="940" height="294" alt="imagen" src="https://github.com/user-attachments/assets/230da8e6-d323-458f-89c2-fcfa9c4d11aa" />

## Cliente solicita un turno
| Elemento | Descripción |
|---|---|
| Servicio que solicita | clientes (puerto 5001), desde POST `/clientes/<id>/solicitar-turno` |
| Servicio que responde | turnos (puerto 5003) |
| Endpoint utilizado | `POST http://turnos:5003/turnos` |
| Información enviada | JSON: `{"cliente_id": <id>, "tramite": <tipo, "general" por defecto>}` |
| Información recibida | 201 con el turno creado: <ul><li>id, codigo (ej. T-001),</li><li>cliente_id,</li><li>asesor_id,</li><li>tramite,</li><li>estado (en_espera)</li><li>creado.</li></ul> También puede recibir 404 (cliente inexistente). |

## Asesor atiende un turno
| Elemento | Descripción |
|---|---|
| Servicio que solicita | asesores (puerto 5002), desde PUT `/asesores/<id>/atender-turno/<turno_id>` |
| Servicio que responde | turnos (puerto 5003) |
| Endpoint utilizado | `PUT http://turnos:5003/turnos/<turno_id>` |
| Información enviada | JSON: `{"asesor_id": <id>, "estado": "en_atencion"}` (el estado puede venir en el body, por defecto en_atencion) |
| Información recibida | 200 con el turno actualizado (asesor asignado y nuevo estado). También puede recibir 400 (estado inválido), 404 (turno o asesor inexistente) o 503 |

## Turno consulta a clientes
| Elemento | Descripción |
|---|---|
| Servicio que solicita | turnos (puerto 5003), al crear un turno (POST /turnos) y al consultar GET /turnos/<id>/detalle |
| Servicio que responde | clientes (puerto 5001) |
| Endpoint utilizado | `GET http://clientes:5001/clientes/<cliente_id>` |
| Información enviada | Solo el id del cliente en la URL (sin body) |
| Información recibida | 200 con los datos del cliente (id, nombre, documento, telefono) o 404 si no existe. Si no responde, turnos devuelve 503. |

## Turnos consulta asesores
| Elemento | Descripción |
|---|---|
| Servicio que solicita | turnos (puerto 5003), al crear o actualizar un turno con asesor_id y en GET /turnos/<id>/detalle |
| Servicio que responde | asesores (puerto 5002) |
| Endpoint utilizado | `GET http://asesores:5002/asesores/<asesor_id>` |
| Información enviada | Solo el id del asesor en la URL (sin body) |
| Información recibida | 200 con los datos del asesor (id, nombre, ventanilla, estado) o 404 si no existe. Si no responde, turnos devuelve 503. |

## DOCKER COMPOSE 
services:
  home:
    build: ./home
    ports:
      - "8080:80"

  mysql_clientes:
    image: mysql:8.0
    container_name: mysql_clientes
    environment:
      MYSQL_ROOT_PASSWORD: ${CLIENTES_DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${CLIENTES_DB_NAME}
      MYSQL_USER: ${CLIENTES_DB_USER}
      MYSQL_PASSWORD: ${CLIENTES_DB_PASSWORD}
    ports:
      - "${CLIENTES_MYSQL_HOST_PORT}:3306"
    volumes:
      - clientes_data:/var/lib/mysql

  clientes:
    build: ./clientes
    container_name: servicio_clientes
    env_file:
      - ./clientes/.env
    ports:
      - "${CLIENTES_PORT}:${CLIENTES_PORT}"
    depends_on:
      - mysql_clientes

  mysql_asesores:
    image: mysql:8.0
    container_name: mysql_asesores
    environment:
      MYSQL_ROOT_PASSWORD: ${ASESORES_DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${ASESORES_DB_NAME}
      MYSQL_USER: ${ASESORES_DB_USER}
      MYSQL_PASSWORD: ${ASESORES_DB_PASSWORD}
    ports:
      - "${ASESORES_MYSQL_HOST_PORT}:3306"
    volumes:
      - asesores_data:/var/lib/mysql

  asesores:
    build: ./asesores
    container_name: servicio_asesores
    env_file:
      - ./asesores/.env
    ports:
      - "${ASESORES_PORT}:${ASESORES_PORT}"
    depends_on:
      - mysql_asesores

  mysql_turnos:
    image: mysql:8.0
    container_name: mysql_turnos
    environment:
      MYSQL_ROOT_PASSWORD: ${TURNOS_DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${TURNOS_DB_NAME}
      MYSQL_USER: ${TURNOS_DB_USER}
      MYSQL_PASSWORD: ${TURNOS_DB_PASSWORD}
    ports:
      - "${TURNOS_MYSQL_HOST_PORT}:3306"
    volumes:
      - turnos_data:/var/lib/mysql

  turnos:
    build: ./turnos
    container_name: servicio_turnos
    env_file:
      - ./turnos/.env
    ports:
      - "${TURNOS_PORT}:${TURNOS_PORT}"
    depends_on:
      - mysql_turnos

volumes:
  clientes_data:
  asesores_data:
  turnos_data:


## DIAGRAMA ACTUALIZADO
<img width="940" height="671" alt="imagen" src="https://github.com/user-attachments/assets/8e73b5f9-c0e3-4a11-bf06-a50693f09f4e" />


# PARTE 1 — ENTENDER EL PROBLEMA

## Paso 1: Responder juntos

## PARTE 1 — ENTENDER EL PROBLEMA

### Paso 1: Responder juntos

#### 1. ¿Qué problema resuelve el sistema?

El sistema distribuido del banco resuelve la gestión desorganizada en la atención al cliente. Estos llegan de manera simultánea a solicitar diferentes trámites como aperturas de cuentas, solicitar documentos, asesoría, transacciones en caja, reclamos, etc. Lo cual genera:

- Filas presenciales abundantes.
- Tiempos de espera inciertos en los puntos físicos.
- Asignación ineficiente de asesores para trámites simples que no requieren atención especializada.
- Falta de información en tiempo real sobre el estado del turno.
- Ausencia de priorización para clientes que requieren atención preferencial.
- Desconocimiento de la sucursal más cercana según su ubicación actual.

Por lo anterior, surge la necesidad de identificar de forma segura al cliente y conectarlo con una sucursal bancaria en un tiempo acertado y un lugar cercano. Nuestro sistema resolverá este problema digitalizando la asignación de turnos: el cliente obtiene un turno, el sistema lo ordena según la prioridad del trámite seleccionado, y lo asigna automáticamente a la ventanilla o asesor disponible, notificando al cliente cuando deba acercarse.

#### 2. ¿Quién lo usará?

- **Clientes del banco:** requieren un servicio presencial, se autentican, solicitan un turno, indican el trámite que desean realizar y reciben notificaciones.
- **Asesores comerciales:** atienden trámites especializados desde su ventanilla, como créditos, tarjetas y cuentas nuevas.
- **Supervisión de sucursales:** monitorea tiempos de atención y disponibilidad del personal.

#### 3. ¿Qué pasaría si no existiera?

- Si el sistema no existiera, se volvería un sistema por orden de llegada, por lo que no se podría diferenciar el tipo de trámite que el cliente necesita.
- Los clientes no sabrían cuándo acercarse, generando aglomeraciones y aumentando el riesgo de errores en el orden de atención.
- No habría trazabilidad de tiempos de espera ni atención, imposibilitando medir la calidad del servicio.
- Habría mala experiencia de usuario, aumentando la probabilidad de conflictos y quejas.

---

# PARTE 2 — IDENTIFICAR LOS SERVICIOS

### Paso 2: Dividir el sistema

Un sistema distribuido se divide en servicios.

- **Servicio de Turnos:** genera el número de turno, define la cola por tipo de servicio y prioridad.
- **Servicio de Clientes:** registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite).
- **Servicio de Cajas:** gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al cajero y registra el cierre de atención.
- **Servicio de Asesores:** gestiona la disponibilidad de los asesores y la atención de trámites especializados.
- **Servicio de Notificaciones:** informa al cliente cuando su turno va a ser atendido y en qué ventanilla.
- **Servicio de Atención:** registra el inicio y finalización de la atención y actualiza el estado del turno.

### 1. ¿Qué funciones principales tiene el sistema?

- Generación de turnos.
- Registro de clientes.
- Asignación de ventanillas.
- Asignación de asesores.
- Gestión del estado de los turnos.
- Notificación al usuario sobre el estado de su turno.

### 2. ¿Qué partes pueden trabajar por separado?

Cada uno de los servicios presentados anteriormente puede trabajar de manera independiente, debido a que cada uno tiene su propia lógica y responsabilidad.

### 3. ¿Qué procesos son independientes?

- El registro de un cliente no depende de que una ventanilla esté libre.
- Una notificación puede reintentarse sin afectar la asignación de turnos.
- La gestión de asesores puede funcionar independientemente del registro de clientes.
- La gestión de cajas puede actualizar la disponibilidad sin modificar directamente los datos de clientes.

---

# PARTE 3 — ¿CÓMO SE COMUNICAN?

## Paso 3: Conexión entre servicios

### ¿Qué servicio necesita información de otro?

- **Turnos necesita información de Clientes** para identificar al cliente y registrar sus datos.
- **Turnos necesita información de Cajas** para saber qué caja está disponible.
- **Turnos necesita información de Asesores** cuando el cliente requiere atención personalizada.
- **Atención necesita información de Turnos** para saber qué cliente debe atender y qué trámite realizará.
- **Notificaciones necesita información de Turnos** para saber qué turno debe notificar y cuándo.

### ¿Quién solicita datos?

El servicio que necesita la información es el que realiza la solicitud.

| Servicio que solicita | Solicita información a |
|---|---|
| Turnos | Clientes |
| Turnos | Cajas |
| Turnos | Asesores |
| Atención | Turnos |
| Notificaciones | Turnos |

### ¿Quién responde?

La comunicación entre los servicios funciona mediante solicitudes y respuestas:

- **Turnos → solicita → Clientes**
- **Clientes → responde → Turnos**

- **Turnos → solicita → Cajas**
- **Cajas → responde → Turnos**

- **Turnos → solicita → Asesores**
- **Asesores → responde → Turnos**

- **Atención → solicita → Turnos**
- **Turnos → responde → Atención**

- **Notificaciones → solicita → Turnos**
- **Turnos → responde → Notificaciones**

### Actualización del estado del turno

Cuando la atención termina:

- **Atención → informa → Turnos**
- **Turnos → actualiza → estado del turno**

De esta manera, los servicios se comunican entre sí sin acceder directamente a las bases de datos de otros servicios.

---

# PARTE 4 — ELEGIR LA ARQUITECTURA

## Paso 4: Tipo de arquitectura

### Arquitectura: Microservicios

La arquitectura seleccionada para el sistema es **Microservicios**, debido a que el sistema se divide en diferentes servicios independientes, cada uno con una responsabilidad específica.

### ¿Cuántos usuarios tendrá el sistema?

Tendrá una cantidad limitada de usuarios, principalmente clientes y empleados que utilizarán el sistema para gestionar y atender los turnos.

### ¿Necesita escalar?

Por ahora no necesita una gran escalabilidad, pero en el futuro podría ampliarse para soportar más usuarios, sucursales y servicios.

### ¿Es un sistema pequeño o grande?

Actualmente es un sistema pequeño, ya que cuenta con seis servicios principales:

- Clientes
- Turnos
- Cajas
- Asesores
- Notificaciones
- Atención

Sin embargo, puede crecer en el futuro agregando nuevas funcionalidades y servicios.

### Justificación de la elección

Elegimos la arquitectura de **microservicios** porque el sistema está dividido en servicios independientes, donde cada uno cumple una función específica. Esto permite que los servicios se comuniquen entre sí y facilita la organización del sistema.

Además, si en el futuro aumenta la cantidad de usuarios o se necesitan nuevas funcionalidades, se pueden ampliar o agregar servicios sin tener que modificar todo el sistema.

---

# PARTE 5 — BASE DE DATOS

## Paso 5: Datos del sistema

### ¿Qué información debe guardarse?

- **Clientes:** Cédula, nombre, tipo de trámite solicitado.
- **Turnos:** Número de turno, categoría/prioridad, estado (en espera, llamado, atendido, cancelado), marca de tiempo.
- **Ventanillas:** Identificador de ventanilla, cajero asignado, estado (libre u ocupada).
- **Notificaciones:** Historial de avisos enviados y su estado de entrega.

### ¿Qué datos son críticos?

El número de turno, su estado y el orden de la cola son críticos: un error aquí implica atender a un cliente fuera de turno. Los datos del cliente (cédula) también son sensibles y deben protegerse.

### ¿Qué pasaría si se pierden?

Se perdería la trazabilidad de quién debía ser atendido y en qué orden, generando reclamos y posible pérdida de confianza del cliente. Por eso se recomienda respaldo periódico (backup) y replicación de la base de datos de Turnos.

### Pregunta clave: ¿una base de datos compartida o una por servicio?

Cada microservicio tendrá su propia base de datos:

- `bd_turnos`
- `bd_clientes`
- `bd_ventanillas`
- `bd_asesores`
- `bd_notificaciones`
- `bd_atencion`

Esto evita el acoplamiento que se genera cuando varios servicios comparten una sola base de datos y permite que cada servicio evolucione su esquema de forma independiente.

La comunicación entre servicios se hace exclusivamente a través de sus **APIs REST**, nunca accediendo directamente a la base de datos de otro servicio.

---

# PARTE 6 — USUARIOS Y ROLES

## Paso 6: Identificar usuarios

### ¿Qué usará el sistema?

- **Cliente:** solicita un turno y consulta su posición en la fila; no puede modificar el estado de otros turnos.
- **Cajero / Asesor (operador):** llama al siguiente turno, marca la atención como finalizada o cancelada.
- **Administrador de sucursal:** crea y edita ventanillas, consulta reportes de tiempos de espera y reasigna las prioridades.
- **Sistema de autoservicio:** actúa como cliente automatizado que genera turnos desde la sucursal física.

### Pregunta clave: ¿todos pueden hacer lo mismo?

No. Se manejan permisos diferenciados por rol:

- El **cliente** solo puede crear y consultar su propio turno.
- El **cajero o asesor** gestiona los turnos asignados a su ventanilla.
- El **administrador** tiene permisos de configuración y gestión del sistema.

---

# PARTE 7 — FALLAS Y RIESGOS

## Paso 7: Pensar como ingenieros reales

### ¿Qué pasaría si falla?

- **Servicio de Turnos:** ningún cliente podría sacar un turno nuevo ni consultar su posición en la fila. Las sucursales tendrían que volver temporalmente a atención por orden de llegada.
- **Base de datos:** se perdería el registro de quién está en la fila y en qué orden, lo que podría hacer que se atienda a alguien fuera de turno o que se dupliquen turnos.
- **Servidor principal:** todo el sistema quedaría inaccesible (clientes, cajeros y administradores), dejando las sucursales sin forma digital de operar.
- **Servicio de Notificaciones:** los clientes no sabrían cuándo acercarse a la ventanilla, generando aglomeraciones y confusión, aunque el resto del sistema siga funcionando.

### ¿Posibles soluciones?

- **Reintentos automáticos:** si una notificación o una llamada a otro servicio falla, el sistema reintentará unas cuantas veces antes de marcarla como fallida.
- **Notificaciones de respaldo:** si falla el canal principal (push/SMS), mostrar el turno también en una pantalla física en la sucursal.
- **Respaldo (backup) y replicación de datos:** copias periódicas de la base de datos de turnos, priorizando por ser la más crítica, para poder restaurar el estado de la cola sin perder información.
- **Modo degradado:** si el servidor principal falla, permitir que las sucursales sigan atendiendo manualmente (papel/orden de llegada) mientras se restablece el sistema.
- **Redundancia del servidor:** tener un servidor secundario que tome el control automáticamente si el principal falla (failover).

---

# PARTE 10 — REVISIÓN DEL EQUIPO

## Revisión de Plataforma de Reservas de Hoteles

### Mejoras

Si es una aplicación que apenas está iniciando, separar la autenticación y la gestión de los usuarios en servicios independientes no es una propuesta totalmente adecuada, ya que puede introducir una alta complejidad innecesaria.

Aunque se puedan ver como dos servicios con funciones diferentes, sería más conveniente mantenerlas juntas inicialmente para evitar la duplicidad de datos, múltiples despliegues y problemas de comunicación entre servicios.

### Correcciones

- En la pregunta **“¿Qué procesos son independientes?”** solo se mencionan Usuarios, Hoteles y Autenticación. Sin embargo, en la pregunta anterior, **“¿Qué partes pueden trabajar por separado?”**, también se incluyen Notificaciones y Reseñas. Por lo tanto, la información no es completamente coherente y se deberían incluir todos los servicios que puedan funcionar de manera independiente.

- Se debería mencionar de forma clara cómo se comunicarán los servicios. Por ejemplo, utilizar **comunicación REST síncrona** para consultas que necesitan una respuesta inmediata, como la consulta de disponibilidad, y **mensajería asíncrona** para procesos como el envío de notificaciones.

- También sería conveniente mencionar el uso de un **API Gateway** como punto de entrada para las solicitudes realizadas por los clientes.

- La comunicación entre servicios está representada actualmente con ejemplos que no corresponden a los servicios definidos, como “Pedidos → solicita → Inventario” y “Pagos → confirma → Pedidos”. Se recomienda reemplazarlos por ejemplos relacionados con la plataforma de reservas:

  - **Reservas → solicita → Disponibilidad**
  - **Reservas → solicita → Hoteles**
  - **Reservas → notifica → Notificaciones**

### Fallos posibles

- **Falta de un servicio de Pagos:** si la plataforma contempla pagos, debería definirse este servicio. De lo contrario, podría presentarse un problema de consistencia, como una reserva confirmada sin que se haya realizado el pago o un pago realizado sin que la reserva haya sido confirmada.

- **Inconsistencia de datos entre microservicios:** al manejar bases de datos independientes, puede existir un fallo en la sincronización entre servicios. Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este último podría no recibir la información de la cancelación y mantener datos desactualizados.

- **Punto único de fallo en Disponibilidad:** si el servicio de Disponibilidad deja de funcionar, el servicio de Reservas no podrá comprobar si una habitación está disponible. Esto podría bloquear temporalmente el proceso de creación de nuevas reservas.

### Confirmar si el diseño tiene sentido

El diseño propuesto sí tiene sentido para una plataforma de reservas de hoteles, porque el sistema puede dividirse en diferentes servicios con responsabilidades específicas, como Usuarios, Autenticación, Hoteles, Disponibilidad, Reservas, Notificaciones y Reseñas.

Sin embargo, se deben tener en cuenta los posibles problemas mencionados anteriormente, especialmente la comunicación entre servicios y la consistencia de los datos cuando cada microservicio maneja su propio almacenamiento.

Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este podría no recibir la información de la cancelación y mantener datos desactualizados.

A partir de lo anterior, se pueden incluir las mejoras y correcciones mencionadas anteriormente, con el fin de hacer que el diseño sea más claro, coherente y adecuado para una arquitectura de microservicios.

### Conclusión

La propuesta es coherente con una arquitectura de microservicios, ya que permite dividir el sistema en servicios independientes que pueden escalar y evolucionar de manera individual.

Sin embargo, es importante definir correctamente las responsabilidades de cada servicio, la comunicación entre ellos, el manejo de fallos y la consistencia de los datos.
