# Guion para Video - Lab 7 Visualizacion de Datos

Duracion maxima recomendada: **7:30 minutos** para dejar margen antes del limite de 8 minutos.

Area asignada: **Area 4. Marketing**

Dashboard: **RetailMax - Dashboard de Marketing**

## Distribucion por Integrante

### Integrante 1 - Introduccion e Infraestructura

Tiempo sugerido: 0:00 a 1:20

Guion:

> Hola, somos el equipo encargado del Area 4: Marketing para RetailMax. Esta area es responsable de disenar y evaluar campanas comerciales, entender el comportamiento de los clientes y encontrar oportunidades para aumentar la respuesta comercial.
>
> Para este laboratorio construimos un ambiente reproducible con Docker Compose. El proyecto levanta PostgreSQL y Metabase con un solo comando: `docker compose up`.
>
> PostgreSQL carga automaticamente los archivos `DDL.sql` y `DATA.sql`, y Metabase queda conectado a la base de datos con el usuario de calificacion `calificar@uvg.edu.gt`.
>
> Nuestro dashboard se llama `RetailMax - Dashboard de Marketing` y esta dividido en dos tabs: `Campanas y Conversion` y `Clientes, Segmentos y Canales`.

Accion en pantalla:

- Mostrar la carpeta del proyecto.
- Mostrar brevemente `docker-compose.yml`.
- Abrir Metabase en `http://localhost:3000`.

## Integrante 2 - Recorrido del Tab 1

Tiempo sugerido: 1:20 a 2:45

Guion:

> El primer tab se llama `Campanas y Conversion`. Su objetivo es medir que tan efectivas son las campanas de Marketing.
>
> Aqui analizamos la tasa de respuesta por campana, el ROI estimado, la conversion por tipo de campana, la respuesta por segmento, la evolucion mensual de contactos y respuestas, y el costo por respuesta.
>
> Todos estos indicadores fueron creados usando consultas SQL nativas en Metabase, no con el constructor visual.
>
> Este tab responde preguntas como: que campanas generan mas respuesta, que tipo de campana conviene repetir, que segmentos reaccionan mejor y que campanas usan mejor el presupuesto.

Accion en pantalla:

- Entrar al tab `Campanas y Conversion`.
- Hacer scroll mostrando los 6 indicadores.
- Abrir una pregunta y mostrar que esta hecha con SQL nativo.

## Integrante 3 - Recorrido del Tab 2

Tiempo sugerido: 2:45 a 4:10

Guion:

> El segundo tab se llama `Clientes, Segmentos y Canales`. Este tab se enfoca en entender el comportamiento de los clientes y encontrar oportunidades para futuras campanas.
>
> Incluye indicadores de valor y frecuencia por segmento, ingresos por canal y segmento, frecuencia mensual de compra, productos mas atractivos para clientes que respondieron, tiendas con mejor respuesta comercial y clientes prioritarios para reactivacion.
>
> Este analisis es importante porque Marketing no solo necesita saber si una campana funciono, sino tambien a que clientes dirigir nuevas promociones, en que canal vender y que productos destacar.

Accion en pantalla:

- Entrar al tab `Clientes, Segmentos y Canales`.
- Mostrar los 6 indicadores.
- Resaltar la tabla de clientes prioritarios para reactivacion.

## Integrante 4 - Top 3 Indicadores

Tiempo sugerido: 4:10 a 6:15

Guion:

> Para el analisis final seleccionamos tres indicadores principales.
>
> El primero es `Tasa de respuesta por campana`, porque mide directamente que campanas lograron que los clientes reaccionaran. Este indicador permite comparar campanas y detectar cuales tuvieron mejor desempeno.
>
> El segundo es `ROI estimado por campana`, porque conecta el presupuesto de Marketing con los ingresos generados durante la vigencia de cada campana. Esto ayuda a decidir donde invertir mas presupuesto.
>
> El tercero es `Productos mas atractivos para clientes que respondieron`, porque muestra que productos compraron los clientes que si respondieron a campanas. Este insight sirve para disenar promociones mas precisas.
>
> En conjunto, estos tres indicadores cubren respuesta, rentabilidad y producto, que son tres dimensiones clave para Marketing.

Accion en pantalla:

- Mostrar cada uno de los 3 indicadores.
- Explicar brevemente el insight que se ve en pantalla.

## Integrante 5 - Indicador Mas Importante y Cierre

Tiempo sugerido: 6:15 a 7:30

Guion:

> Consideramos que el indicador mas importante es `ROI estimado por campana`.
>
> La razon es que una campana puede tener muchas respuestas, pero si no genera suficientes ingresos en relacion con su presupuesto, no necesariamente es una buena decision comercial.
>
> Este indicador ayuda a Marketing a priorizar campanas rentables, justificar presupuesto y mejorar la estrategia futura. Tambien permite comparar campanas de distintos tipos, como email, redes sociales, SMS o descuento directo.
>
> En conclusion, el dashboard permite que RetailMax evalue campanas, entienda mejor a sus clientes y encuentre oportunidades concretas para aumentar la efectividad comercial. Todo el ambiente queda reproducible con Docker Compose y todos los indicadores estan sustentados con SQL nativo.

Accion en pantalla:

- Mostrar el indicador `ROI estimado por campana`.
- Volver al dashboard completo.
- Cerrar recordando que el repositorio incluye `docker-compose.yml`, `metabase-data`, `informe.pdf` y `README.md`.

## Checklist Antes de Grabar

- Docker Desktop esta corriendo.
- El comando `docker compose up` levanta sin errores.
- Metabase abre en `http://localhost:3000`.
- Se puede entrar con `calificar@uvg.edu.gt` y `secret123+`.
- El dashboard tiene 2 tabs.
- Cada tab tiene 6 indicadores.
- Al menos una pregunta muestra claramente la consulta SQL nativa.
- Todos los integrantes hablan y aparecen en el video.
- El video dura menos de 8 minutos.

