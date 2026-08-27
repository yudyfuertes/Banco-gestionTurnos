# Banco-gestionTurnos

# PARTE 1 — ENTENDER EL PROBLEMA

## Paso 1: Responder juntos

### 1. ¿Qué problema resuelve el sistema?

El sistema distribuido del banco resuelve la gestión desorganizada en la atención al cliente. Estos llegan de manera simultánea a solicitar diferentes trámites, como aperturas de cuentas, solicitud de documentos, asesoría, transacciones en caja, reclamos, etc. Lo cual genera:

- Filas presenciales abundantes.
- Tiempos de espera inciertos en los puntos físicos.
- Asignación ineficiente de asesores para trámites simples que no requieren atención especializada.
- Falta de información en tiempo real sobre el estado del turno.
- Ausencia de priorización para clientes que requieren atención preferencial.
- Desconocimiento de la sucursal más cercana según su ubicación actual.

Por lo anterior, surge la necesidad de identificar de forma segura al cliente y conectarlo con una sucursal bancaria en un tiempo acertado y un lugar cercano. Nuestro sistema resolverá este problema digitalizando la asignación de turnos: el cliente obtiene un turno, el sistema lo ordena según la prioridad del trámite seleccionado y lo asigna automáticamente a la ventanilla o asesor disponible, notificando al cliente cuando deba acercarse.

### 2. ¿Quién lo usará?

- **Clientes del banco:** requieren un servicio presencial. Se autentican, solicitan un turno, indican el trámite que desean realizar y reciben notificaciones.
- **Asesores comerciales:** atienden trámites especializados desde su ventanilla, como créditos, tarjetas y cuentas nuevas.
- **Supervisión de sucursales:** monitorea tiempos de atención y disponibilidad del personal.

### 3. ¿Qué pasaría si no existiera?

- Si el sistema no existiera, se volvería a un sistema por orden de llegada, por lo que no se podría diferenciar el tipo de trámite que el cliente necesita.
- Los clientes no sabrían cuándo acercarse, generando aglomeraciones y aumentando el riesgo de errores en el orden de atención.
- No habría trazabilidad de tiempos de espera ni atención, imposibilitando medir la calidad del servicio.
- Habría una mala experiencia de usuario, aumentando la probabilidad de conflictos y quejas.

---

# PARTE 2 — IDENTIFICAR LOS SERVICIOS

## Paso 2: Dividir el sistema

Un sistema distribuido se divide en servicios.

### Servicios principales

- **Servicio de Turnos:** genera el número de turno y define la cola según el tipo de servicio y prioridad.
- **Servicio de Clientes:** registra y valida los datos del cliente, como tipo de documento, número de documento, celular y tipo de trámite.
- **Servicio de Asesores:** gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al cajero y registra el cierre de atención.
- **Servicio de Notificaciones:** informa al cliente cuando su turno va a ser atendido y en qué ventanilla.

### 1. ¿Qué funciones principales tiene el sistema?

- Generación de turnos.
- Registro de clientes.
- Asignación de ventanillas.
- Notificación al usuario sobre el estado de su turno.

### 2. ¿Qué partes pueden trabajar por separado?

Cada uno de los servicios presentados anteriormente puede trabajar de manera independiente, debido a que cada uno tiene su propia lógica.

### 3. ¿Qué procesos son independientes?

- El registro de un cliente no depende de que una ventanilla esté libre.
- Una notificación puede reintentarse sin afectar la asignación de turnos.

---

# PARTE 3 — ¿CÓMO SE COMUNICAN?

## Paso 3: Conexión entre servicios

### ¿Qué servicio necesita información de otro?

- **Turnos** necesita información de **Clientes** para identificar al cliente y registrar sus datos.
- **Turnos** necesita información de **Cajas** para saber qué caja está disponible.
- **Turnos** necesita información de **Asesores** cuando el cliente requiere atención personalizada.
- **Atención** necesita información de **Turnos** para saber qué cliente debe atender y qué trámite realizará.
- **Notificaciones** necesita información de **Turnos** para saber qué turno debe notificar y cuándo.

### ¿Quién solicita datos?

El servicio que necesita la información es el que realiza la solicitud.

- **Turnos** solicita → **Clientes**
- **Turnos** solicita → **Cajas**
- **Turnos** solicita → **Asesores**
- **Atención** solicita → **Turnos**
- **Notificaciones** solicita → **Turnos**

### ¿Quién responde?

- **Turnos** → solicita → **Clientes**
- **Clientes** → responde → **Turnos**

- **Turnos** → solicita → **Cajas**
- **Cajas** → responde → **Turnos**

- **Turnos** → solicita → **Asesores**
- **Asesores** → responde → **Turnos**

- **Atención** → solicita → **Turnos**
- **Turnos** → responde → **Atención**

- **Notificaciones** → solicita → **Turnos**
- **Turnos** → responde → **Notificaciones**

### Comunicación adicional

Cuando la atención termina:

- **Atención** → informa → **Turnos**
- **Turnos** → actualiza → **estado del turno**

---

# PARTE 4 — ELEGIR LA ARQUITECTURA

## Paso 4: Tipo de arquitectura

**Arquitectura elegida: Microservicios**

### Preguntas guía

#### ¿Cuántos usuarios tendrá el sistema?

Tendrá una **cantidad limitada de usuarios**, principalmente clientes y empleados que utilizarán el sistema para gestionar y atender los turnos.

#### ¿Necesita escalar?

**Por ahora no necesita una gran escalabilidad**, pero en el futuro podría ampliarse para soportar más usuarios, sucursales y servicios.

#### ¿Es un sistema pequeño o grande?

Actualmente es un **sistema pequeño**, ya que cuenta con seis servicios principales: **Clientes, Turnos, Cajas, Asesores, Notificaciones y Atención**. Sin embargo, puede crecer en el futuro agregando nuevas funcionalidades.

### Justificación de la elección

Elegimos la arquitectura de **microservicios** porque el sistema está dividido en servicios independientes, donde cada uno cumple una función específica. Esto permite que los servicios se comuniquen entre sí y facilita la organización del sistema.

Además, si en el futuro aumenta la cantidad de usuarios o se necesitan nuevas funcionalidades, se pueden ampliar o agregar servicios sin tener que modificar todo el sistema.

---

# PARTE 5 — BASE DE DATOS

## Paso 5: Datos del sistema

### ¿Qué información debe guardarse?

- **Clientes:** cédula, nombre y tipo de trámite solicitado.
- **Turnos:** número de turno, categoría/prioridad, estado (en espera, llamado, atendido, cancelado) y marca de tiempo.
- **Ventanillas:** identificador de ventanilla, cajero asignado y estado (libre u ocupada).
- **Notificaciones:** historial de avisos enviados y su estado de entrega.

### ¿Qué datos son críticos?

El número de turno, su estado y el orden de la cola son críticos, ya que un error en estos datos podría provocar que se atienda a un cliente fuera de turno.

Los datos del cliente, como la cédula, también son sensibles y deben protegerse adecuadamente.

### ¿Qué pasaría si se pierden?

Se perdería la trazabilidad de quién debía ser atendido y en qué orden, generando reclamos y una posible pérdida de confianza del cliente. Por eso, se recomienda realizar respaldos periódicos (backup) y utilizar replicación de la base de datos de Turnos.

### Pregunta clave: ¿una base de datos compartida o una por servicio?

Cada microservicio tendrá su propia base de datos:

- **bd_turnos**
- **bd_clientes**
- **bd_ventanillas**
- **bd_notificaciones**

Esto permite evitar el acoplamiento que se genera cuando varios servicios comparten una sola base de datos y permite que cada servicio evolucione su esquema de forma independiente.

La comunicación entre servicios se realiza exclusivamente a través de sus **APIs REST**, sin acceder directamente a la base de datos de otro servicio.

---

# PARTE 6 — USUARIOS Y ROLES

## Paso 6: Identificar usuarios

### ¿Quién usará el sistema?

- **Cliente:** solicita un turno y consulta su posición en la fila; no puede modificar el estado de otros turnos.
- **Cajero / Asesor (operador):** llama al siguiente turno y marca la atención como finalizada o cancelada.
- **Administrador de sucursal:** crea y edita ventanillas, consulta reportes de tiempos de espera y reasigna las prioridades.
- **Sistema de autoservicio:** actúa como cliente automatizado que genera turnos desde la sucursal física.

### Pregunta clave: ¿todos pueden hacer lo mismo?

No. Se manejan permisos diferenciados según el rol:

- El **cliente** solo puede consultar o crear su propio turno.
- El **cajero** solo gestiona los turnos asignados a su ventanilla.
- El **administrador** tiene permisos de configuración y administración del sistema.
