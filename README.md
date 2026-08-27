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
