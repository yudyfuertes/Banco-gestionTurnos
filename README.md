# Banco-gestionTurnos

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
