# Banco-gestionTurnos

PARTE 1 — ENTENDER EL PROBLEMA

Paso 1: Responder juntos
1.	¿Qué problema resuelve el sistema?

El sistema distribuido del banco resuelve la gestión desorganizada en la atención al cliente, estos llegan de manera simultánea a solicitar diferentes trámites como lo son las aperturas de cuentas, solicitar documentos,  asesoría, transacciones en caja, reclamos, etc. Lo cual genera: 

- Filas presenciales abundantes
- Tiempos de espera inciertos en los puntos físicos
- Asignación ineficiente de asesores para trámites simples que no requieren atención especializada.
- Falta de información en tiempo real sobre el estado del turno
- Ausencia de priorización para clientes que requieren atención preferencial 
- Desconocimiento de la sucursal más cercana según su ubicación actual.

Por lo anterior, surge la necesidad de identificar de forma segura al cliente y conectarlo con una sucursal bancaria en un tiempo acertado y un lugar cercano. Nuestro sistema resolverá este problema digitalizando la asignación de turnos: el cliente obtiene un turno, el sistema lo ordena según la prioridad del trámite seleccionado, y lo asigna automáticamente a la ventanilla o asesor disponible, notificando al cliente cuando deba acercarse. 

2.	¿Quién lo usará?
   
-	Clientes del banco que requieren un servicio presencial.
Se autentican, solicitan un turno, indican el trámite que sean realizar y recibir notificaciones.
-	Asesores comerciales: atienden tramites especializados desde su ventanilla (créditos, tarjetas, cuentas nuevas)
-	Supervisión de sucursales: Monitorea tiempos de atención y disponibilidad del personal

3.	¿Qué pasaría si no existiera?
   
- Si el sistema no existiera, se volvería un sistema por orden de llegada, por lo que no se podría diferenciar el tipo de trámite que el cliente necesita.
- Los clientes no sabrían cuando acercarse, generando aglomeraciones, y aumentando el riesgo de errores en el orden de atención.
- No habría trazabilidad de tiempos de espera ni atención, imposibilitando medir la calidad del servicio.
- Habría mala experiencia de usuario, aumentando la probabilidad de conflictos y quejas.

PARTE 2 – IDENTIFICAR LOS SERVICIOS
Paso 2: Dividir el sistema
Un sistema distribuido se divide en servicios.
Preguntas guía:
-	Servicio de turnos: genera el número de turno, define la cola por tipo de servicio y prioridad.
-	Servicio de clientes: Registra y valida los datos del cliente (tipo de documento, número de documento, celular, tipo de trámite) 
-	Servicio de asesores: Gestiona el estado de cada ventanilla (disponible/ocupada), asigna el turno al cajero y registra el cierre de atención.
-	Servicio de notificaciones: Informa al cliente cuando su turno va a ser atendido y en que ventanilla. 
  
1. ¿Qué funciones principales tiene el sistema?
-	Generación de turnos
-	Registro de clientes 
-	Asignación de ventanillas 
-	Notificación al usuario el estado de su turno

2. ¿Qué partes pueden trabajar por separado?
   
Cada uno de los servicios presentados anteriormente puede trabajar de manera independiente, debido a que cada uno tiene su propia lógica.

3. ¿Qué procesos son independientes?

-	El registro de un cliente no depende de que una ventanilla este libre.
-	Una notificación puede reintentarse sin afectar la asignación de turnos.
PARTE 5 – BASE DE DATOS
Paso 5: Datos del sistema
¿Qué información debe guardarse?
•	Clientes: Cédula, nombre, tipo de trámite solicitado.
•	Turnos: Número de turno, categoría/prioridad, estado (en espera, llamado, atendido, cancelado), marca de tiempo.
•	Ventanillas: Identificador de ventanilla, cajero asignado, estado (libre u ocupada).
•	Notificaciones: Historial de avisos enviados y su estado de entrega.
¿Qué datos son críticos?: El número de turno, su estado y el orden de la cola son críticos: un error aquí implica atender a un cliente fuera de turno. Los datos del cliente (cédula) también son sensibles y deben protegerse.
¿Qué pasaría si se pierden? Se perdería la trazabilidad de quién debía ser atendido y en qué orden, generando reclamos y posible pérdida de confianza del cliente; por eso se recomienda respaldo periódico (backup) y replicación de la base de datos de Turnos
Pregunta clave: ¿una base de datos compartida o una por servicio?: Cada microservicio tendrá su propia base de datos (bd_turnos, bd_clientes, bd_ventanillas, bd_notificaciones), evitando el acoplamiento que se genera cuando varios servicios comparten una sola base de datos y permitiendo que cada uno evolucione su esquema de forma independiente. La comunicación entre servicios se hace exclusivamente a través de sus APIS REST, nunca accediendo directamente a la base de datos de otro servicio.

PARTE 6 – USUARIOS Y ROLES
Paso 6: Identificar usuarios
¿Que usará el sistema?
•	Cliente: Solicita un turno y consulta su posición en la fila; no puede modificar el estado de otros turnos.
•	Cajero / Asesor (operador): Llama al siguiente turno, marca la atención como finalizada o cancelada.
•	Administrador de sucursal: Crea y edita ventanillas, consulta reportes de tiempos de espera, reasigna las prioridades.
•	Sistema de autoservicio: Actúa como cliente automatizado que genera turnos desde la sucursal física.
Pregunta clave: ¿todos pueden hacer lo mismo? No, se manejan permisos diferenciados por el rol, el cliente solo lee o crea su propio turno, el cajero solo gestiona los turnos asignados a su ventanilla y solo el administrador tiene permisos de configuración del sistema.

PARTE 7 — FALLAS Y RIESGO
 
Paso 7: Pensar como ingenieros reales
 
¿Qué pasaría si falla?
 
El servicio de turnos: ningún cliente podría sacar turno nuevo ni consultar su posición en la fila; las sucursales tendrían que volver temporalmente a atención por orden de llegada.
La base de datos: se perdería el registro de quién está en la fila y en qué orden, lo que podría hacer que se atienda a alguien fuera de turno o que se dupliquen turnos.
El servidor principal: todo el sistema quedaría inaccesible (clientes, cajeros y administradores), dejando las sucursales sin forma digital de operar.
El servicio de notificaciones: los clientes no sabrían cuándo acercarse a la ventanilla, generando aglomeraciones y confusión, aunque el resto del sistema siga funcionando.
 
¿Posibles soluciones?
 
Reintentos automáticos: si una notificación o una llamada a otro servicio falla, el sistema reintentar unas cuantas veces antes de marcarla como fallida.
Notificaciones de respaldo: si falla el canal principal (push/SMS), mostrar el turno también en una pantalla física en la sucursal.
Respaldo (backup) y replicación de datos: copias periódicas de la base de datos de turnos, priorizando por ser la más crítica, para poder restaurar el estado de la cola sin perder información.
Modo degradado: si el servidor principal falla, permitir que las sucursales sigan atendiendo manualmente (papel/orden de llegada) mientras se restablece el sistema.
Redundancia del servidor: tener un servidor secundario que tome el control automáticamente si el principal falla (failover)

PARTE 10 — REVISIÓN DEL EQUIPO

Revisión de Plataforma de reservas de Hoteles:

Mejoras: 

Si es una aplicación que apenas está iniciando, separar la autenticación y la gestión de los usuarios en servicios independientes no es una propuesta totalmente adecuada, puede introducir una alta complejidad innecesaria. Aunque se puedan ver como dos servicios con funciones diferentes, sería más conveniente mantenerlas juntas inicialmente para evitar la duplicidad de datos, múltiples despliegues, y problemas de comunicación entre servicios. 

Correcciones: 
En la pregunta “¿Qué procesos son independientes?” solo se mencionan Usuarios, Hoteles y Autenticación. Sin embargo, en la pregunta anterior, “¿Qué partes pueden trabajar por separado?”, también se incluyen Notificaciones y Reseñas. Por lo tanto, la información no es completamente coherente y se deberían incluir todos los servicios que puedan funcionar de manera independiente.


Se debería mencionar de forma clara cómo se comunicarán los servicios. Por ejemplo, utilizar comunicación REST síncrona para consultas que necesitan una respuesta inmediata, como la consulta de disponibilidad, y mensajería asíncrona para procesos como el envío de notificaciones. También sería conveniente mencionar el uso de un API Gateway como punto de entrada para las solicitudes realizadas por los clientes.


La comunicación entre servicios está representada actualmente con ejemplos que no corresponden a los servicios definidos, como “Pedidos → solicita → Inventario” y “Pagos → confirma → Pedidos”. Se recomienda reemplazarlos por ejemplos relacionados con la plataforma de reservas, como:

 Reservas → solicita → Disponibilidad
 Reservas → solicita → Hoteles
 Reservas → notifica → Notificaciones
Fallos posibles 
Falta de un servicio de Pagos: Si la plataforma contempla pagos, debería definirse este servicio. De lo contrario, podría presentarse un problema de consistencia, como una reserva confirmada sin que se haya realizado el pago o un pago realizado sin que la reserva haya sido confirmada.


Inconsistencia de datos entre microservicios: Al manejar bases de datos independientes, puede existir un fallo en la sincronización entre servicios. Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este último podría no recibir la información de la cancelación y mantener datos desactualizados.


Punto único de fallo en Disponibilidad: Si el servicio de Disponibilidad deja de funcionar, el servicio de Reservas no podrá comprobar si una habitación está disponible. Esto podría bloquear temporalmente el proceso de creación de nuevas reservas.

Confirmar si el diseño tiene sentido
El diseño propuesto sí tiene sentido para una plataforma de reservas de hoteles, porque el sistema puede dividirse en diferentes servicios con responsabilidades específicas, como Usuarios, Autenticación, Hoteles, Disponibilidad, Reservas, Notificaciones y Reseñas.
Sin embargo, se deben tener en cuenta los posibles problemas mencionados anteriormente, especialmente la comunicación entre servicios y la consistencia de los datos cuando cada microservicio maneja su propio almacenamiento.
Por ejemplo, si un usuario cancela una reserva y el servicio de Reservas actualiza correctamente la información, pero la comunicación con el servicio de Notificaciones falla, este podría no recibir la información de la cancelación y mantener datos desactualizados.
A partir de lo anterior, se pueden incluir las mejoras y correcciones mencionadas anteriormente, con el fin de hacer que el diseño sea más claro, coherente y adecuado para una arquitectura de microservicios.
En conclusión, la propuesta es coherente con una arquitectura de microservicios, ya que permite dividir el sistema en servicios independientes que pueden escalar y evolucionar de manera individual. Sin embargo, es importante definir correctamente las responsabilidades de cada servicio, la comunicación entre ellos, el manejo de los datos, el API Gateway y, si aplica, el servicio de Pagos, para reducir posibles fallos en el funcionamiento del sistema.

