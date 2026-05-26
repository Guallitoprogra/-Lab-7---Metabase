# Lab 7 - Visualizacion de Datos

Proyecto del laboratorio de Bases de Datos 1 para desplegar una solucion reproducible de visualizacion de datos con PostgreSQL y Metabase usando Docker Compose.

Area asignada: **Area 4. Marketing**

El dashboard esta enfocado en disenar y evaluar campanas comerciales, entender el comportamiento de clientes, analizar segmentos, frecuencia de compra, productos atractivos, tiendas con mejor respuesta, canales de venta y oportunidades para nuevas campanas.

## Estructura del Proyecto

```text
.
|-- docker-compose.yml
|-- README.md
|-- informe.md
|-- informe.pdf
|-- metabase-data/
|-- scripts/
|   `-- setup_metabase.py
`-- sql/
    |-- 01_DDL.sql
    `-- 02_DATA.sql
```

## Requisitos

- Docker Desktop instalado.
- Docker Desktop encendido antes de ejecutar el proyecto.
- Docker Compose disponible desde la terminal.
- Puerto `3000` libre para Metabase.
- Puerto `5432` libre para PostgreSQL.


## Como Correr el Laboratorio

Desde la carpeta raiz del repositorio, ejecutar solamente:

```bash
docker compose up
```

Ese comando levanta:

- PostgreSQL.
- Metabase.
- Un servicio auxiliar que configura Metabase automaticamente.

PostgreSQL carga automaticamente los archivos:

- `sql/01_DDL.sql`
- `sql/02_DATA.sql`

Metabase queda disponible en:

```text
http://localhost:3000
```

## Credenciales de Metabase

Usuario para calificacion:

```text
Correo: calificar@uvg.edu.gt
Contrasena: secret123+
```


## Tabs del Dashboard

### 1. Campanas y Conversion

Este tab mide la efectividad de las campanas comerciales. Incluye indicadores de respuesta, conversion, retorno estimado, evolucion mensual y costo por respuesta.

Indicadores:

1. Tasa de respuesta por campana.
2. ROI estimado por campana.
3. Conversion por tipo de campana.
4. Respuesta por segmento de cliente.
5. Evolucion mensual de contactos y respuestas.
6. Costo por respuesta por campana.

### 2. Clientes, Segmentos y Canales

Este tab analiza el comportamiento comercial de clientes y segmentos para detectar oportunidades de campanas futuras.

Indicadores:

1. Valor y frecuencia por segmento.
2. Ingresos por canal y segmento.
3. Frecuencia de compra mensual por segmento.
4. Productos mas atractivos para clientes que respondieron.
5. Tiendas con mejor respuesta comercial.
6. Clientes prioritarios para reactivacion.

## Como Entrar a Metabase

1. Ejecutar:

```bash
docker compose up
```

2. Abrir el navegador en:

```text
http://localhost:3000
```

3. Iniciar sesion con:

```text
calificar@uvg.edu.gt
secret123+
```

4. Abrir el dashboard:

```text
RetailMax - Dashboard de Marketing
```

## Si Docker No Levanta

Primero confirmar que Docker Desktop este abierto y corriendo.

Luego revisar contenedores:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs
```

Si los puertos estan ocupados, cerrar otros servicios que usen `3000` o `5432`.

Para reiniciar desde cero:

```bash
docker compose down -v
```

En PowerShell, tambien se puede limpiar el volumen local de Metabase:

```powershell
Remove-Item -Recurse -Force .\metabase-data\*
docker compose up
```


## Video de Presentacion

Enlace video:




