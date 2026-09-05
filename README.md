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

