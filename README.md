SISTEMA DISTRIBUIDO DE GESTION DE TURNOS BANCARIOS

1. ENTENDER EL PROBLEMA

¿Qué problema resuelve el sistema?

El sistema distribuido del banco resuelve la gestión desorganizada en la atención al cliente. Los clientes llegan de manera simultánea a solicitar diferentes trámites (apertura de cuentas, solicitud de documentos, asesoría, transacciones en caja, reclamos, etc.), lo cual genera:

- Filas presenciales abundantes.
- Tiempos de espera inciertos en los puntos físicos.
- Asignación ineficiente de asesores para trámites simples que no requieren atención especializada.
- Falta de información en tiempo real sobre el estado del turno.
- Ausencia de priorización para clientes que requieren atención preferencial.
- Desconocimiento de la sucursal más cercana según la ubicación actual del cliente.

Surge entonces la necesidad de identificar de forma segura al cliente y conectarlo con una sucursal bancaria en un tiempo acertado y un lugar cercano. El sistema resuelve este problema digitalizando la asignación de turnos: el cliente obtiene un turno, el sistema lo ordena según la prioridad del trámite seleccionado y lo asigna automáticamente a la ventanilla o asesor disponible, notificando al cliente cuando deba acercarse.

¿Quién lo usará?

- Clientes del banco: se autentican, solicitan un turno, indican el trámite a realizar y reciben notificaciones.
- Asesores comerciales: atienden trámites especializados desde su ventanilla (créditos, tarjetas, cuentas nuevas).
- Supervisión de sucursales: monitorea tiempos de atención y disponibilidad del personal.

¿Qué pasaría si no existiera?

- Se volvería un sistema por orden de llegada, sin diferenciar el tipo de trámite que necesita el cliente.
- Los clientes no sabrían cuándo acercarse, generando aglomeraciones y aumentando el riesgo de errores en el orden de atención.
- No habría trazabilidad de tiempos de espera ni de atención, imposibilitando medir la calidad del servicio.
- Habría mala experiencia de usuario, aumentando la probabilidad de conflictos y quejas.


2. IDENTIFICAR LOS SERVICIOS

Servicios principales

- Servicio de Turnos: genera el número de turno, define la cola por tipo de servicio y prioridad.
- Servicio de Clientes: registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite).
- Servicio de Asesores: gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al cajero y registra el cierre de atención.
- Servicio de Notificaciones: informa al cliente cuándo su turno va a ser atendido y en qué ventanilla.

Funciones principales del sistema

- Generación de turnos.
- Registro de clientes.
- Asignación de ventanillas.
- Notificación al usuario sobre el estado de su turno.

¿Qué partes pueden trabajar por separado?

Cada uno de los servicios presentados puede trabajar de manera independiente, ya que cada uno tiene su propia lógica de negocio.

¿Qué procesos son independientes?

- El registro de un cliente no depende de que una ventanilla esté libre.
- Una notificación puede reintentarse sin afectar la asignación de turnos.


3. BASE DE DATOS

¿Qué información debe guardarse?

- Clientes: cédula, nombre, tipo de trámite solicitado.
- Turnos: número de turno, categoría/prioridad, estado (en espera, llamado, atendido, cancelado), marca de tiempo.
- Ventanillas: identificador de ventanilla, cajero asignado, estado (libre u ocupada).
- Notificaciones: historial de avisos enviados y su estado de entrega.

¿Qué datos son críticos?

El número de turno, su estado y el orden de la cola son críticos: un error aquí implica atender a un cliente fuera de turno. Los datos del cliente (cédula) también son sensibles y deben protegerse.

¿Qué pasaría si se pierden?

Se perdería la trazabilidad de quién debía ser atendido y en qué orden, generando reclamos y posible pérdida de confianza del cliente. Por eso se recomienda respaldo periódico (backup) y replicación de la base de datos de Turnos.

¿Base de datos compartida o una por servicio?

Cada microservicio tendrá su propia base de datos: bd_turnos, bd_clientes, bd_ventanillas y bd_notificaciones. Esto evita el acoplamiento que se genera cuando varios servicios comparten una sola base de datos y permite que cada uno evolucione su esquema de forma independiente. La comunicación entre servicios se hace exclusivamente a través de sus APIs REST, nunca accediendo directamente a la base de datos de otro servicio.


4. USUARIOS Y ROLES

- Cliente: solicita un turno y consulta su posición en la fila; no puede modificar el estado de otros turnos.
- Cajero / Asesor (operador): llama al siguiente turno, marca la atención como finalizada o cancelada.
- Administrador de sucursal: crea y edita ventanillas, consulta reportes de tiempos de espera, reasigna prioridades.
- Sistema de autoservicio: actúa como cliente automatizado que genera turnos desde la sucursal física.

¿Todos pueden hacer lo mismo?

No. Se manejan permisos diferenciados por rol: el cliente solo lee o crea su propio turno, el cajero solo gestiona los turnos asignados a su ventanilla, y solo el administrador tiene permisos de configuración del sistema.


5. FALLAS Y RIESGOS

¿Qué pasaría si falla...?

- El Servicio de Turnos: ningún cliente podría sacar turno nuevo ni consultar su posición en la fila; las sucursales tendrían que volver temporalmente a atención por orden de llegada.
- La base de datos: se perdería el registro de quién está en la fila y en qué orden, pudiendo atender a alguien fuera de turno o duplicar turnos.
- El servidor principal: todo el sistema quedaría inaccesible (clientes, cajeros y administradores), dejando las sucursales sin forma digital de operar.
- El Servicio de Notificaciones: los clientes no sabrían cuándo acercarse a la ventanilla, generando aglomeraciones y confusión, aunque el resto del sistema siga funcionando.

Posibles soluciones

- Reintentos automáticos: si una notificación o una llamada a otro servicio falla, el sistema reintenta unas cuantas veces antes de marcarla como fallida.
- Notificaciones de respaldo: si falla el canal principal (push/SMS), mostrar el turno también en una pantalla física en la sucursal.
- Backup y replicación de datos: copias periódicas de la base de datos de turnos (la más crítica), para restaurar el estado de la cola sin perder información.
- Modo degradado: si el servidor principal falla, permitir que las sucursales sigan atendiendo manualmente (papel/orden de llegada) mientras se restablece el sistema.
- Redundancia del servidor: tener un servidor secundario que tome el control automáticamente si el principal falla (failover).


6. REVISIÓN DE DISEÑO: PLATAFORMA DE RESERVAS DE HOTELES

Revisión cruzada realizada al diseño propuesto por otro equipo para una plataforma de reservas de hoteles.

Mejoras sugeridas

Si la aplicación apenas está iniciando, separar la autenticación y la gestión de usuarios en servicios independientes no es del todo adecuado; puede introducir complejidad innecesaria. Aunque cumplen funciones distintas, es más conveniente mantenerlas juntas inicialmente para evitar duplicidad de datos, múltiples despliegues y problemas de comunicación entre servicios.

Correcciones

En la pregunta "¿Qué procesos son independientes?" solo se mencionan Usuarios, Hoteles y Autenticación, pero en la pregunta anterior ("¿Qué partes pueden trabajar por separado?") también se incluyen Notificaciones y Reseñas. Se recomienda incluir todos los servicios que puedan funcionar de manera independiente para mantener coherencia.

Se debería mencionar de forma clara cómo se comunicarán los servicios. Por ejemplo, utilizar comunicación REST síncrona para consultas que necesitan una respuesta inmediata, como la consulta de disponibilidad, y mensajería asíncrona para procesos como el envío de notificaciones. También sería conveniente mencionar el uso de un API Gateway como punto de entrada para las solicitudes realizadas por los clientes.

La comunicación entre servicios está representada actualmente con ejemplos que no corresponden a los servicios definidos, como "Pedidos solicita a Inventario" y "Pagos confirma a Pedidos". Se recomienda reemplazarlos por ejemplos relacionados con la plataforma de reservas, como:

- Reservas solicita a Disponibilidad
- Reservas solicita a Hoteles
- Reservas notifica a Notificaciones

Posibles fallos

- Falta de un servicio de Pagos: si la plataforma contempla pagos, debería definirse este servicio. De lo contrario, podría presentarse un problema de consistencia, como una reserva confirmada sin que se haya realizado el pago, o un pago realizado sin que la reserva haya sido confirmada.

- Inconsistencia de datos entre microservicios: al manejar bases de datos independientes, puede existir un fallo en la sincronización entre servicios. Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este último podría no recibir la información de la cancelación y mantener datos desactualizados.

- Punto único de fallo en Disponibilidad: si el servicio de Disponibilidad deja de funcionar, el servicio de Reservas no podrá comprobar si una habitación está disponible. Esto podría bloquear temporalmente el proceso de creación de nuevas reservas.

¿El diseño tiene sentido?

El diseño propuesto sí tiene sentido para una plataforma de reservas de hoteles, porque el sistema puede dividirse en diferentes servicios con responsabilidades específicas, como Usuarios, Autenticación, Hoteles, Disponibilidad, Reservas, Notificaciones y Reseñas. Sin embargo, se deben tener en cuenta los posibles problemas mencionados anteriormente, especialmente la comunicación entre servicios y la consistencia de los datos cuando cada microservicio maneja su propio almacenamiento. Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este podría no recibir la información de la cancelación y mantener datos desactualizados.

Conclusión

La propuesta es coherente con una arquitectura de microservicios, ya que permite dividir el sistema en servicios independientes que pueden escalar y evolucionar de manera individual. Sin embargo, es importante definir correctamente las responsabilidades de cada servicio, la comunicación entre ellos, el manejo de los datos, el API Gateway y, si aplica, el servicio de Pagos, para reducir posibles fallos en el funcionamiento del sistema.
