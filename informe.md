# Informe - Lab 7 Visualizacion de Datos

Area asignada: **Area 4. Marketing**

Dashboard: **RetailMax - Dashboard de Marketing**

Todos los indicadores se construyen con Native Query / SQL en Metabase.

## Tab 1: Campanas y Conversion

### 1. Tasa de respuesta por campana

Representa el porcentaje de clientes contactados que respondieron a cada campana. Es importante porque permite comparar que campanas generan mayor reaccion comercial. Visualizacion sugerida: grafica de barras, porque facilita ordenar y comparar campanas por tasa de respuesta.

```sql
SELECT
    c.nombre AS campana,
    c.tipo,
    c.canal,
    COUNT(cc.id_cliente) AS clientes_contactados,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS clientes_respondieron,
    ROUND(100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(cc.id_cliente), 0), 2) AS tasa_respuesta_pct
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.id_campana, c.nombre, c.tipo, c.canal
ORDER BY tasa_respuesta_pct DESC;
```

### 2. ROI estimado por campana

Representa la relacion entre ingresos atribuidos durante la vigencia de la campana y su presupuesto. Es importante porque Marketing necesita priorizar campanas que convierten presupuesto en ventas. Visualizacion sugerida: barras, porque permite identificar rapidamente las campanas con mejor retorno.

```sql
SELECT
    c.nombre AS campana,
    c.presupuesto,
    COALESCE(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 0) AS ingresos_atribuidos,
    ROUND((COALESCE(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 0) - c.presupuesto) / NULLIF(c.presupuesto, 0), 2) AS roi_estimado
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
LEFT JOIN pedido p
    ON p.id_cliente = cc.id_cliente
   AND p.fecha BETWEEN c.fecha_inicio AND c.fecha_fin
   AND p.estado = 'completado'
LEFT JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
GROUP BY c.id_campana, c.nombre, c.presupuesto
ORDER BY roi_estimado DESC;
```

### 3. Conversion por tipo de campana

Representa la tasa de conversion agregada por tipo de campana: email, redes sociales, SMS o descuento directo. Es importante para decidir que canales tacticos conviene repetir. Visualizacion sugerida: barras, porque compara categorias discretas.

```sql
SELECT
    c.tipo,
    COUNT(cc.id_cliente) AS clientes_contactados,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS clientes_respondieron,
    ROUND(100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(cc.id_cliente), 0), 2) AS tasa_conversion_pct
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.tipo
ORDER BY tasa_conversion_pct DESC;
```

### 4. Respuesta por segmento de cliente

Representa como responden los segmentos VIP, regular y nuevo a las campanas. Es importante porque permite personalizar mensajes y ofertas segun el perfil del cliente. Visualizacion sugerida: barras, porque muestra diferencias claras entre segmentos.

```sql
SELECT
    cl.segmento,
    COUNT(*) AS contactos,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas,
    ROUND(100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS tasa_respuesta_pct
FROM campana_cliente cc
JOIN cliente cl ON cl.id_cliente = cc.id_cliente
GROUP BY cl.segmento
ORDER BY tasa_respuesta_pct DESC;
```

### 5. Evolucion mensual de contactos y respuestas

Representa la cantidad mensual de clientes contactados y clientes que respondieron. Es importante para detectar estacionalidad y meses con mayor actividad comercial. Visualizacion sugerida: linea, porque muestra tendencias en el tiempo.

```sql
SELECT
    DATE_TRUNC('month', c.fecha_inicio)::date AS mes,
    COUNT(cc.id_cliente) AS contactos,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY DATE_TRUNC('month', c.fecha_inicio)
ORDER BY mes;
```

### 6. Costo por respuesta por campana

Representa cuanto presupuesto se invierte por cada respuesta obtenida. Es importante porque mide eficiencia de gasto de Marketing. Visualizacion sugerida: barras ordenadas ascendentemente, porque menor costo por respuesta indica mejor eficiencia.

```sql
SELECT
    c.nombre AS campana,
    c.presupuesto,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas,
    ROUND(c.presupuesto / NULLIF(SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END), 0), 2) AS costo_por_respuesta
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.id_campana, c.nombre, c.presupuesto
ORDER BY costo_por_respuesta ASC NULLS LAST;
```

## Tab 2: Clientes, Segmentos y Canales

### 7. Valor y frecuencia por segmento

Representa clientes con compra, pedidos, frecuencia, ticket promedio e ingresos por segmento. Es importante para identificar segmentos con mayor valor comercial. Visualizacion sugerida: barras o tabla resumida, porque combina volumen y valor.

```sql
SELECT
    cl.segmento,
    COUNT(DISTINCT cl.id_cliente) AS clientes_con_compra,
    COUNT(DISTINCT p.id_pedido) AS pedidos_completados,
    ROUND(COUNT(DISTINCT p.id_pedido)::numeric / NULLIF(COUNT(DISTINCT cl.id_cliente), 0), 2) AS frecuencia_promedio,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)) / NULLIF(COUNT(DISTINCT p.id_pedido), 0), 2) AS ticket_promedio,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ingresos
FROM cliente cl
JOIN pedido p ON p.id_cliente = cl.id_cliente AND p.estado = 'completado'
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
GROUP BY cl.segmento
ORDER BY ingresos DESC;
```

### 8. Ingresos por canal y segmento

Representa ingresos de ventas completadas por canal y segmento. Es importante para definir si una campana debe enfocarse en tienda, online o en ambos canales. Visualizacion sugerida: barras agrupadas o apiladas.

```sql
SELECT
    p.canal,
    cl.segmento,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ingresos
FROM pedido p
JOIN cliente cl ON cl.id_cliente = p.id_cliente
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY p.canal, cl.segmento
ORDER BY p.canal, ingresos DESC;
```

### 9. Frecuencia de compra mensual por segmento

Representa pedidos por cliente activo cada mes para cada segmento. Es importante para entender cambios de comportamiento y programar campanas en momentos de menor frecuencia. Visualizacion sugerida: linea, porque compara tendencias mensuales.

```sql
SELECT
    DATE_TRUNC('month', p.fecha)::date AS mes,
    cl.segmento,
    COUNT(DISTINCT p.id_pedido) AS pedidos,
    COUNT(DISTINCT p.id_cliente) AS clientes_activos,
    ROUND(COUNT(DISTINCT p.id_pedido)::numeric / NULLIF(COUNT(DISTINCT p.id_cliente), 0), 2) AS pedidos_por_cliente
FROM pedido p
JOIN cliente cl ON cl.id_cliente = p.id_cliente
WHERE p.estado = 'completado'
GROUP BY DATE_TRUNC('month', p.fecha), cl.segmento
ORDER BY mes, cl.segmento;
```

### 10. Productos mas atractivos para clientes que respondieron

Representa los productos con mayor ingreso entre clientes que respondieron a una campana y compraron durante su vigencia. Es importante para disenar ofertas con productos probados en audiencias receptivas. Visualizacion sugerida: barras horizontales.

```sql
SELECT
    pr.nombre AS producto,
    ca.nombre AS categoria,
    COUNT(DISTINCT p.id_cliente) AS clientes_respondedores,
    SUM(dp.cantidad) AS unidades,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ingresos
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana AND cc.respondio = TRUE
JOIN pedido p
    ON p.id_cliente = cc.id_cliente
   AND p.fecha BETWEEN c.fecha_inicio AND c.fecha_fin
   AND p.estado = 'completado'
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = dp.id_producto
JOIN categoria ca ON ca.id_categoria = pr.id_categoria
GROUP BY pr.id_producto, pr.nombre, ca.nombre
ORDER BY ingresos DESC
LIMIT 15;
```

### 11. Tiendas con mejor respuesta comercial

Representa tiendas y regiones donde clientes que respondieron a campanas realizaron compras durante la vigencia de la campana. Es importante para coordinar activaciones regionales y reforzar tiendas con mejor respuesta. Visualizacion sugerida: barras por tienda.

```sql
SELECT
    t.region,
    t.nombre AS tienda,
    COUNT(DISTINCT p.id_cliente) AS clientes_respondedores_con_compra,
    COUNT(DISTINCT p.id_pedido) AS pedidos,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ingresos
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana AND cc.respondio = TRUE
JOIN pedido p
    ON p.id_cliente = cc.id_cliente
   AND p.fecha BETWEEN c.fecha_inicio AND c.fecha_fin
   AND p.estado = 'completado'
JOIN tienda t ON t.id_tienda = p.id_tienda
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
GROUP BY t.region, t.nombre
ORDER BY ingresos DESC;
```

### 12. Clientes prioritarios para reactivacion

Representa clientes con alto valor historico pero sin compras recientes. Es importante para campanas de recuperacion, cupones personalizados o mensajes de retencion. Visualizacion sugerida: tabla, porque Marketing necesita ver nombre, segmento, ciudad y valor historico para accionar.

```sql
WITH historial AS (
    SELECT
        cl.id_cliente,
        cl.nombre,
        cl.segmento,
        cl.ciudad,
        MAX(p.fecha) AS ultima_compra,
        COUNT(DISTINCT p.id_pedido) AS pedidos,
        ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS valor_historico
    FROM cliente cl
    JOIN pedido p ON p.id_cliente = cl.id_cliente AND p.estado = 'completado'
    JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
    GROUP BY cl.id_cliente, cl.nombre, cl.segmento, cl.ciudad
)
SELECT
    nombre,
    segmento,
    ciudad,
    ultima_compra,
    pedidos,
    valor_historico
FROM historial
WHERE ultima_compra < DATE '2026-02-01'
  AND valor_historico >= 3000
ORDER BY valor_historico DESC
LIMIT 20;
```

