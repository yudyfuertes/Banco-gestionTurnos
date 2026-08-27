# Sistema Distribuido de Gestión de Turnos Bancarios

Diseño de arquitectura de microservicios para la gestión de turnos y atención al cliente en sucursales bancarias.

---

## Tabla de Contenidos

1. [Entender el Problema](#1-entender-el-problema)
2. [Identificar los Servicios](#2-identificar-los-servicios)
3. [Base de Datos](#3-base-de-datos)
4. [Usuarios y Roles](#4-usuarios-y-roles)
5. [Fallas y Riesgos](#5-fallas-y-riesgos)
6. [Revisión de Diseño: Plataforma de Reservas de Hoteles](#6-revisión-de-diseño-plataforma-de-reservas-de-hoteles)

---

## 1. Entender el Problema

### ¿Qué problema resuelve el sistema?

El sistema distribuido del banco resuelve la gestión desorganizada en la atención al cliente. Los clientes llegan de manera simultánea a solicitar diferentes trámites (apertura de cuentas, solicitud de documentos, asesoría, transacciones en caja, reclamos, etc.), lo cual genera:

- Filas presenciales abundantes.
- Tiempos de espera inciertos en los puntos físicos.
- Asignación ineficiente de asesores para trámites simples que no requieren atención especializada.
- Falta de información en tiempo real sobre el estado del turno.
- Ausencia de priorización para clientes que requieren atención preferencial.
- Desconocimiento de la sucursal más cercana según la ubicación actual del cliente.

Surge entonces la necesidad de identificar de forma segura al cliente y conectarlo con una sucursal bancaria en un tiempo acertado y un lugar cercano. El sistema resuelve este problema **digitalizando la asignación de turnos**: el cliente obtiene un turno, el sistema lo ordena según la prioridad del trámite seleccionado y lo asigna automáticamente a la ventanilla o asesor disponible, notificando al cliente cuando deba acercarse.

### ¿Quién lo usará?

| Actor | Uso |
|---|---|
| **Clientes del banco** | Se autentican, solicitan un turno, indican el trámite a realizar y reciben notificaciones. |
| **Asesores comerciales** | Atienden trámites especializados desde su ventanilla (créditos, tarjetas, cuentas nuevas). |
| **Supervisión de sucursales** | Monitorea tiempos de atención y disponibilidad del personal. |

### ¿Qué pasaría si no existiera?

- Se volvería un sistema por orden de llegada, sin diferenciar el tipo de trámite que necesita el cliente.
- Los clientes no sabrían cuándo acercarse, generando aglomeraciones y aumentando el riesgo de errores en el orden de atención.
- No habría trazabilidad de tiempos de espera ni de atención, imposibilitando medir la calidad del servicio.
- Habría mala experiencia de usuario, aumentando la probabilidad de conflictos y quejas.

---

## 2. Identificar los Servicios

### Servicios principales

| Servicio | Responsabilidad |
|---|---|
| **Servicio de Turnos** | Genera el número de turno, define la cola por tipo de servicio y prioridad. |
| **Servicio de Clientes** | Registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite). |
| **Servicio de Asesores** | Gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al cajero y registra el cierre de atención. |
| **Servicio de Notificaciones** | Informa al cliente cuándo su turno va a ser atendido y en qué ventanilla. |

### Funciones principales del sistema

- Generación de turnos.
- Registro de clientes.
- Asignación de ventanillas.
- Notificación al usuario sobre el estado de su turno.

### ¿Qué partes pueden trabajar por separado?

Cada uno de los servicios presentados puede trabajar de manera independiente, ya que cada uno tiene su propia lógica de negocio.

### ¿Qué procesos son independientes?

- El registro de un cliente no depende de que una ventanilla esté libre.
- Una notificación puede reintentarse sin afectar la asignación de turnos.

---

## 3. Base de Datos

### ¿Qué información debe guardarse?

| Entidad | Datos almacenados |
|---|---|
| **Clientes** | Cédula, nombre, tipo de trámite solicitado. |
| **Turnos** | Número de turno, categoría/prioridad, estado (en espera, llamado, atendido, cancelado), marca de tiempo. |
| **Ventanillas** | Identificador de ventanilla, cajero asignado, estado (libre u ocupada). |
| **Notificaciones** | Historial de avisos enviados y su estado de entrega. |

### ¿Qué datos son críticos?

El **número de turno, su estado y el orden de la cola** son críticos: un error aquí implica atender a un cliente fuera de turno. Los datos del cliente (cédula) también son sensibles y deben protegerse.

### ¿Qué pasaría si se pierden?

Se perdería la trazabilidad de quién debía ser atendido y en qué orden, generando reclamos y posible pérdida de confianza del cliente. Por eso se recomienda **respaldo periódico (backup)** y **replicación** de la base de datos de Turnos.

### ¿Base de datos compartida o una por servicio?

Cada microservicio tendrá su **propia base de datos**:

- `bd_turnos`
- `bd_clientes`
- `bd_ventanillas`
- `bd_notificaciones`

Esto evita el acoplamiento que se genera cuando varios servicios comparten una sola base de datos y permite que cada uno evolucione su esquema de forma independiente. La comunicación entre servicios se hace **exclusivamente a través de sus APIs REST**, nunca accediendo directamente a la base de datos de otro servicio.

---

## 4. Usuarios y Roles

| Rol | Permisos |
|---|---|
| **Cliente** | Solicita un turno y consulta su posición en la fila; no puede modificar el estado de otros turnos. |
| **Cajero / Asesor (operador)** | Llama al siguiente turno, marca la atención como finalizada o cancelada. |
| **Administrador de sucursal** | Crea y edita ventanillas, consulta reportes de tiempos de espera, reasigna prioridades. |
| **Sistema de autoservicio** | Actúa como cliente automatizado que genera turnos desde la sucursal física. |

### ¿Todos pueden hacer lo mismo?

No. Se manejan permisos diferenciados por rol:

- El cliente solo lee o crea su propio turno.
- El cajero solo gestiona los turnos asignados a su ventanilla.
- Solo el administrador tiene permisos de configuración del sistema.

---

## 5. Fallas y Riesgos

### ¿Qué pasaría si falla...?

| Componente | Impacto |
|---|---|
| **Servicio de Turnos** | Ningún cliente podría sacar turno nuevo ni consultar su posición en la fila; las sucursales tendrían que volver temporalmente a atención por orden de llegada. |
| **Base de datos** | Se perdería el registro de quién está en la fila y en qué orden, pudiendo atender a alguien fuera de turno o duplicar turnos. |
| **Servidor principal** | Todo el sistema quedaría inaccesible (clientes, cajeros y administradores), dejando las sucursales sin forma digital de operar. |
| **Servicio de Notificaciones** | Los clientes no sabrían cuándo acercarse a la ventanilla, generando aglomeraciones y confusión, aunque el resto del sistema siga funcionando. |

### Posibles soluciones

- **Reintentos automáticos**: si una notificación o una llamada a otro servicio falla, el sistema reintenta unas cuantas veces antes de marcarla como fallida.
- **Notificaciones de respaldo**: si falla el canal principal (push/SMS), mostrar el turno también en una pantalla física en la sucursal.
- **Backup y replicación de datos**: copias periódicas de la base de datos de turnos (la más crítica), para restaurar el estado de la cola sin perder información.
- **Modo degradado**: si el servidor principal falla, permitir que las sucursales sigan atendiendo manualmente (papel/orden de llegada) mientras se restablece el sistema.
- **Redundancia del servidor**: tener un servidor secundario que tome el control automáticamente si el principal falla (failover).

---

## 6. Revisión de Diseño: Plataforma de Reservas de Hoteles

Revisión cruzada realizada al diseño propuesto por otro equipo para una plataforma de reservas de hoteles.

### Mejoras sugeridas

- **Autenticación y Usuarios**: si la aplicación apenas está iniciando, separar la autenticación y la gestión de usuarios en servicios independientes no es del todo adecuado; puede introducir complejidad innecesaria. Aunque cumplen funciones distintas, es más conveniente mantenerlas juntas inicialmente para evitar duplicidad de datos, múltiples despliegues y problemas de comunicación entre servicios.

### Correcciones

- **Inconsistencia en "procesos independientes"**: en la pregunta *"¿Qué procesos son independientes?"* solo se mencionan Usuarios, Hoteles y Autenticación, pero en la pregunta anterior (*"¿Qué partes pueden trabajar por separado?"*) también se incluyen Notificaciones y Reseñas. Se recomienda incluir todos los servicios que puedan funcionar de manera independiente para mantener coherencia.

- **Comunicación entre servicios**: se debe especificar claramente cómo se comunicarán los servicios, por ejemplo:
  - Comunicación **REST síncrona** para consultas que necesitan respuesta inmediata (ej. disponibilidad).
  - **Mensajería asíncrona** para procesos como el envío de notificaciones.
  - Uso de un **API Gateway** como punto de entrada único para las solicitudes de los clientes.

- **Ejemplos de comunicación incorrectos**: actualmente se usan ejemplos que no corresponden a los servicios definidos (Pedidos → solicita → Inventario, Pagos → confirma → Pedidos). Se recomienda reemplazarlos por ejemplos propios de la plataforma de reservas:
  - Reservas → solicita → Disponibilidad
  - Reservas → solicita → Hoteles
  - Reservas → notifica → Notificaciones

### Posibles fallos identificados

| Riesgo | Descripción |
|---|---|
| **Falta de servicio de Pagos** | Si la plataforma contempla pagos, debe definirse este servicio explícitamente. De lo contrario puede haber inconsistencias, como una reserva confirmada sin pago realizado, o un pago realizado sin reserva confirmada. |
| **Inconsistencia de datos entre microservicios** | Al manejar bases de datos independientes puede fallar la sincronización. Ej: si un usuario cancela una reserva y el servicio de Reservas se actualiza correctamente, pero la comunicación con Notificaciones falla, este último podría mantener datos desactualizados. |
| **Punto único de fallo en Disponibilidad** | Si el servicio de Disponibilidad deja de funcionar, Reservas no podrá comprobar si una habitación está disponible, bloqueando temporalmente la creación de nuevas reservas. |

### ¿El diseño tiene sentido?

Sí. El diseño propuesto tiene sentido para una plataforma de reservas de hoteles, porque el sistema puede dividirse en servicios con responsabilidades específicas: **Usuarios, Autenticación, Hoteles, Disponibilidad, Reservas, Notificaciones y Reseñas**.

Sin embargo, deben atenderse los problemas señalados, especialmente:

- La comunicación entre servicios.
- La consistencia de los datos cuando cada microservicio maneja su propio almacenamiento (ej. una cancelación que no se propaga correctamente a Notificaciones).

### Conclusión

La propuesta es coherente con una arquitectura de microservicios, ya que permite dividir el sistema en servicios independientes que pueden escalar y evolucionar de manera individual. Sin embargo, es importante definir correctamente:

- Las responsabilidades de cada servicio.
- La comunicación entre ellos.
- El manejo de los datos.
- El API Gateway.
- El servicio de Pagos (si aplica).

Esto con el fin de reducir posibles fallos en el funcionamiento del sistema.
