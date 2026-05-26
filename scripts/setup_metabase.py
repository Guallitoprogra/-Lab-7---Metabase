import json
import os
import sys
import time
import urllib.error
import urllib.request


BASE_URL = os.environ.get("METABASE_URL", "http://metabase:3000").rstrip("/")
ADMIN_EMAIL = os.environ["MB_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["MB_ADMIN_PASSWORD"]


def request(method, path, payload=None, token=None, retries=30):
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Metabase-Session"] = token
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    url = f"{BASE_URL}{path}"
    last_error = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code not in (404, 409, 422):
                last_error = f"{method} {path} -> HTTP {exc.code}: {body}"
                time.sleep(2)
                continue
            raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from exc
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(2)
    raise RuntimeError(f"No response from Metabase after retries: {last_error}")


def optional(method, path, payload=None, token=None):
    try:
        return request(method, path, payload, token, retries=1)
    except Exception as exc:
        print(f"Optional step failed for {method} {path}: {exc}")
        return None


def ensure_setup():
    props = request("GET", "/api/session/properties")
    setup_token = props.get("setup-token")
    if setup_token:
        payload = {
            "token": setup_token,
            "user": {
                "email": ADMIN_EMAIL,
                "first_name": "Usuario",
                "last_name": "Calificador",
                "password": ADMIN_PASSWORD,
            },
            "prefs": {
                "site_name": "RetailMax Marketing Analytics",
                "site_locale": "es",
                "allow_tracking": False,
            },
            "database": {
                "engine": "postgres",
                "name": "RetailMax PostgreSQL",
                "details": {
                    "host": os.environ["PG_HOST"],
                    "port": int(os.environ["PG_PORT"]),
                    "dbname": os.environ["PG_DB"],
                    "user": os.environ["PG_USER"],
                    "password": os.environ["PG_PASSWORD"],
                    "ssl": False,
                    "tunnel-enabled": False,
                },
                "auto_run_queries": True,
                "is_full_sync": True,
                "is_on_demand": False,
                "schedules": {},
            },
        }
        optional("POST", "/api/setup", payload)

    session = request("POST", "/api/session", {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    return session["id"]


def list_items(path, token):
    response = request("GET", path, token=token)
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    return response if isinstance(response, list) else []


def get_database_id(token):
    for db in list_items("/api/database", token):
        if db.get("name") == "RetailMax PostgreSQL":
            return db["id"]
    payload = {
        "engine": "postgres",
        "name": "RetailMax PostgreSQL",
        "details": {
            "host": os.environ["PG_HOST"],
            "port": int(os.environ["PG_PORT"]),
            "dbname": os.environ["PG_DB"],
            "user": os.environ["PG_USER"],
            "password": os.environ["PG_PASSWORD"],
            "ssl": False,
            "tunnel-enabled": False,
        },
        "auto_run_queries": True,
        "is_full_sync": True,
        "is_on_demand": False,
        "schedules": {},
    }
    return request("POST", "/api/database", payload, token)["id"]


INDICATORS = [
    {
        "tab": "Campañas y Conversión",
        "name": "Tasa de respuesta por campaña",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Campañas y Conversión",
        "name": "ROI estimado por campaña",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Campañas y Conversión",
        "name": "Conversión por tipo de campaña",
        "display": "bar",
        "query": """
SELECT
    c.tipo,
    COUNT(cc.id_cliente) AS clientes_contactados,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS clientes_respondieron,
    ROUND(100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(cc.id_cliente), 0), 2) AS tasa_conversion_pct
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.tipo
ORDER BY tasa_conversion_pct DESC;
""",
    },
    {
        "tab": "Campañas y Conversión",
        "name": "Respuesta por segmento de cliente",
        "display": "bar",
        "query": """
SELECT
    cl.segmento,
    COUNT(*) AS contactos,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas,
    ROUND(100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS tasa_respuesta_pct
FROM campana_cliente cc
JOIN cliente cl ON cl.id_cliente = cc.id_cliente
GROUP BY cl.segmento
ORDER BY tasa_respuesta_pct DESC;
""",
    },
    {
        "tab": "Campañas y Conversión",
        "name": "Evolución mensual de contactos y respuestas",
        "display": "line",
        "query": """
SELECT
    DATE_TRUNC('month', c.fecha_inicio)::date AS mes,
    COUNT(cc.id_cliente) AS contactos,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY DATE_TRUNC('month', c.fecha_inicio)
ORDER BY mes;
""",
    },
    {
        "tab": "Campañas y Conversión",
        "name": "Costo por respuesta por campaña",
        "display": "bar",
        "query": """
SELECT
    c.nombre AS campana,
    c.presupuesto,
    SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas,
    ROUND(c.presupuesto / NULLIF(SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END), 0), 2) AS costo_por_respuesta
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.id_campana, c.nombre, c.presupuesto
ORDER BY costo_por_respuesta ASC NULLS LAST;
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Valor y frecuencia por segmento",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Ingresos por canal y segmento",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Frecuencia de compra mensual por segmento",
        "display": "line",
        "query": """
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
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Productos más atractivos para clientes que respondieron",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Tiendas con mejor respuesta comercial",
        "display": "bar",
        "query": """
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
""",
    },
    {
        "tab": "Clientes, Segmentos y Canales",
        "name": "Clientes prioritarios para reactivación",
        "display": "table",
        "query": """
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
""",
    },
]


def ensure_card(indicator, database_id, token):
    for card in list_items("/api/card", token):
        if card.get("name") == indicator["name"]:
            return card["id"]
    payload = {
        "name": indicator["name"],
        "display": indicator["display"],
        "dataset_query": {
            "database": database_id,
            "type": "native",
            "native": {"query": indicator["query"].strip()},
        },
        "visualization_settings": {},
        "description": f"Indicador de Marketing - {indicator['tab']}",
    }
    return request("POST", "/api/card", payload, token)["id"]


def ensure_dashboard(token):
    for dashboard in list_items("/api/dashboard", token):
        if dashboard.get("name") == "RetailMax - Dashboard de Marketing":
            return dashboard["id"]
    payload = {
        "name": "RetailMax - Dashboard de Marketing",
        "description": "Dashboard para diseñar y evaluar campañas comerciales, segmentación de clientes, canales y oportunidades de marketing.",
        "parameters": [],
    }
    return request("POST", "/api/dashboard", payload, token)["id"]


def ensure_tabs(dashboard_id, token):
    dashboard = request("GET", f"/api/dashboard/{dashboard_id}", token=token)
    existing = {tab.get("name"): tab.get("id") for tab in dashboard.get("tabs", [])}
    result = {}
    for name in ["Campañas y Conversión", "Clientes, Segmentos y Canales"]:
        if name in existing:
            result[name] = existing[name]
            continue
        tab = optional("POST", f"/api/dashboard/{dashboard_id}/tabs", {"name": name}, token)
        if tab and tab.get("id"):
            result[name] = tab["id"]
    return result


def dashboard_has_card(dashboard_id, card_id, token):
    dashboard = request("GET", f"/api/dashboard/{dashboard_id}", token=token)
    for dashcard in dashboard.get("dashcards", []) or []:
        card = dashcard.get("card") or {}
        if card.get("id") == card_id or dashcard.get("card_id") == card_id:
            return True
    return False


def add_cards(dashboard_id, card_ids, tab_ids, token):
    dashboard = request("GET", f"/api/dashboard/{dashboard_id}", token=token)
    if len(dashboard.get("dashcards", []) or []) >= len(INDICATORS):
        return

    positions = {
        "Campañas y Conversión": [(0, 0), (12, 0), (0, 6), (12, 6), (0, 12), (12, 12)],
        "Clientes, Segmentos y Canales": [(0, 0), (12, 0), (0, 6), (12, 6), (0, 12), (12, 12)],
    }
    counters = {"Campañas y Conversión": 0, "Clientes, Segmentos y Canales": 0}
    temp_tabs = {
        "Campañas y Conversión": -1,
        "Clientes, Segmentos y Canales": -2,
    }
    tabs_payload = [
        {"id": tab_ids.get("Campañas y Conversión", temp_tabs["Campañas y Conversión"]), "name": "Campañas y Conversión"},
        {"id": tab_ids.get("Clientes, Segmentos y Canales", temp_tabs["Clientes, Segmentos y Canales"]), "name": "Clientes, Segmentos y Canales"},
    ]
    cards_payload = []
    for indicator in INDICATORS:
        card_id = card_ids[indicator["name"]]
        tab = indicator["tab"]
        col, row = positions[tab][counters[tab]]
        counters[tab] += 1
        cards_payload.append({
            "id": -(len(cards_payload) + 1),
            "card_id": card_id,
            "row": row,
            "col": col,
            "size_x": 12,
            "size_y": 6,
            "parameter_mappings": [],
            "visualization_settings": {},
            "series": [],
            "dashboard_tab_id": tab_ids.get(tab, temp_tabs[tab]),
        })
    request("PUT", f"/api/dashboard/{dashboard_id}/cards", {"cards": cards_payload, "tabs": tabs_payload}, token)


def main():
    print("Configuring Metabase...")
    token = ensure_setup()
    database_id = get_database_id(token)
    optional("POST", f"/api/database/{database_id}/sync_schema", token=token)
    card_ids = {indicator["name"]: ensure_card(indicator, database_id, token) for indicator in INDICATORS}
    dashboard_id = ensure_dashboard(token)
    tab_ids = ensure_tabs(dashboard_id, token)
    add_cards(dashboard_id, card_ids, tab_ids, token)
    print("Metabase configuration finished.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Metabase setup failed: {exc}", file=sys.stderr)
        sys.exit(1)
