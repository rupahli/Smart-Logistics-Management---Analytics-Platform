import pandas as pd


def get_delivery_performance_metrics(cursor, connection):
    query = """
        SELECT s.origin, s.destination,
               ROUND(AVG(DATEDIFF(s.delivery_date, s.order_date)), 2) AS avg_delivery_days,
               ROUND(AVG(COALESCE(r.avg_time_hours, 0) / 24.0), 2) AS expected_days,
               COUNT(s.shipment_id) AS shipment_count
        FROM shipments s
        LEFT JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        WHERE s.delivery_date IS NOT NULL AND s.order_date IS NOT NULL
        GROUP BY s.origin, s.destination
        ORDER BY avg_delivery_days DESC
    """
    cursor.execute(query)
    delivery_summary = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "avg_delivery_days", "expected_days", "shipment_count"],
    )

    delayed_query = """
        SELECT s.origin, s.destination,
               ROUND(AVG(DATEDIFF(s.delivery_date, s.order_date) - COALESCE(r.avg_time_hours, 0) / 24.0), 2) AS delay_days,
               COUNT(s.shipment_id) AS shipment_count
        FROM shipments s
        LEFT JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        WHERE s.delivery_date IS NOT NULL AND s.order_date IS NOT NULL
        GROUP BY s.origin, s.destination
        ORDER BY delay_days DESC
    """
    cursor.execute(delayed_query)
    delayed_routes = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "delay_days", "shipment_count"],
    )

    comparison_query = """
        SELECT s.origin, s.destination,
               ROUND(AVG(DATEDIFF(s.delivery_date, s.order_date)), 2) AS avg_delivery_days,
               ROUND(AVG(COALESCE(r.distance_km, 0)), 2) AS distance_km
        FROM shipments s
        LEFT JOIN routes r ON s.origin = r.origin AND s.destination = r.destination
        WHERE s.delivery_date IS NOT NULL AND s.order_date IS NOT NULL
        GROUP BY s.origin, s.destination
        ORDER BY distance_km DESC
    """
    cursor.execute(comparison_query)
    distance_comparison = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "avg_delivery_days", "distance_km"],
    )

    return {
        "delivery_summary": delivery_summary,
        "delayed_routes": delayed_routes,
        "distance_comparison": distance_comparison,
    }


def get_courier_performance_metrics(cursor, connection):
    query = """
        SELECT s.courier_id, cs.name,
               COUNT(s.shipment_id) AS shipments_handled,
               ROUND(100.0 * SUM(CASE WHEN s.status = 'Delivered' THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS on_time_pct,
               ROUND(AVG(cs.rating), 1) AS avg_rating
        FROM shipments s
        LEFT JOIN courier_staff cs ON s.courier_id = cs.courier_id
        GROUP BY s.courier_id, cs.name
        ORDER BY shipments_handled DESC
    """
    cursor.execute(query)
    return pd.DataFrame(
        cursor.fetchall(),
        columns=["courier_id", "name", "shipments_handled", "on_time_pct", "avg_rating"],
    )


def get_cost_analytics_metrics(cursor, connection):
    total_cost_query = """
        SELECT s.shipment_id, s.origin, s.destination,
               ROUND(COALESCE(c.fuel_cost, 0) + COALESCE(c.labor_cost, 0) + COALESCE(c.misc_cost, 0), 2) AS total_cost,
               ROUND(COALESCE(c.fuel_cost, 0), 2) AS fuel_cost,
               ROUND(COALESCE(c.labor_cost, 0), 2) AS labor_cost,
               ROUND(COALESCE(c.misc_cost, 0), 2) AS misc_cost
        FROM shipments s
        LEFT JOIN costs c ON s.shipment_id = c.shipment_id
        ORDER BY total_cost DESC
    """
    cursor.execute(total_cost_query)
    cost_per_shipment = pd.DataFrame(
        cursor.fetchall(),
        columns=["shipment_id", "origin", "destination", "total_cost", "fuel_cost", "labor_cost", "misc_cost"],
    )

    route_cost_query = """
        SELECT s.origin, s.destination,
               ROUND(SUM(COALESCE(c.fuel_cost, 0) + COALESCE(c.labor_cost, 0) + COALESCE(c.misc_cost, 0)), 2) AS route_cost,
               COUNT(s.shipment_id) AS shipment_count
        FROM shipments s
        LEFT JOIN costs c ON s.shipment_id = c.shipment_id
        GROUP BY s.origin, s.destination
        ORDER BY route_cost DESC
    """
    cursor.execute(route_cost_query)
    cost_per_route = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "route_cost", "shipment_count"],
    )

    cost_mix_query = """
        SELECT ROUND(SUM(COALESCE(c.fuel_cost, 0)) / NULLIF(SUM(COALESCE(c.fuel_cost, 0) + COALESCE(c.labor_cost, 0) + COALESCE(c.misc_cost, 0)), 0) * 100, 2) AS fuel_pct,
               ROUND(SUM(COALESCE(c.labor_cost, 0)) / NULLIF(SUM(COALESCE(c.fuel_cost, 0) + COALESCE(c.labor_cost, 0) + COALESCE(c.misc_cost, 0)), 0) * 100, 2) AS labor_pct
        FROM costs c
    """
    cursor.execute(cost_mix_query)
    cost_mix = pd.DataFrame(cursor.fetchall(), columns=["fuel_pct", "labor_pct"])

    return {
        "cost_per_shipment": cost_per_shipment,
        "cost_per_route": cost_per_route,
        "cost_mix": cost_mix,
        "high_cost_shipments": cost_per_shipment.head(10),
    }


def get_cancellation_analysis_metrics(cursor, connection):
    origin_query = """
        SELECT s.origin,
               ROUND(100.0 * SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS cancellation_rate,
               COUNT(s.shipment_id) AS shipment_count
        FROM shipments s
        GROUP BY s.origin
        ORDER BY cancellation_rate DESC
    """
    cursor.execute(origin_query)
    cancellation_by_origin = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "cancellation_rate", "shipment_count"],
    )

    courier_query = """
        SELECT s.courier_id, cs.name,
               ROUND(100.0 * SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS cancellation_rate,
               COUNT(s.shipment_id) AS shipment_count
        FROM shipments s
        LEFT JOIN courier_staff cs ON s.courier_id = cs.courier_id
        GROUP BY s.courier_id, cs.name
        ORDER BY cancellation_rate DESC
    """
    cursor.execute(courier_query)
    cancellation_by_courier = pd.DataFrame(
        cursor.fetchall(),
        columns=["courier_id", "name", "cancellation_rate", "shipment_count"],
    )

    time_query = """
        SELECT s.shipment_id, s.origin, s.destination, s.order_date,
               MIN(st.timestamp) AS cancellation_time,
               DATEDIFF(MIN(st.timestamp), s.order_date) AS days_to_cancel
        FROM shipments s
        JOIN shipment_tracking st ON s.shipment_id = st.shipment_id
        WHERE st.status = 'Cancelled'
        GROUP BY s.shipment_id, s.origin, s.destination, s.order_date
        ORDER BY days_to_cancel DESC
    """
    cursor.execute(time_query)
    time_to_cancellation = pd.DataFrame(
        cursor.fetchall(),
        columns=["shipment_id", "origin", "destination", "order_date", "cancellation_time", "days_to_cancel"],
    )

    return {
        "cancellation_by_origin": cancellation_by_origin,
        "cancellation_by_courier": cancellation_by_courier,
        "time_to_cancellation": time_to_cancellation,
    }


def get_warehouse_insights_metrics(cursor, connection):
    query = """
        SELECT w.warehouse_id, w.city, w.capacity,
               SUM(CASE WHEN s.origin = w.city THEN 1 ELSE 0 END) AS origin_shipments,
               SUM(CASE WHEN s.destination = w.city THEN 1 ELSE 0 END) AS destination_shipments,
               SUM(CASE WHEN s.origin = w.city THEN 1 ELSE 0 END) + SUM(CASE WHEN s.destination = w.city THEN 1 ELSE 0 END) AS traffic_count
        FROM warehouses w
        LEFT JOIN shipments s ON s.origin = w.city OR s.destination = w.city
        GROUP BY w.warehouse_id, w.city, w.capacity
        ORDER BY traffic_count DESC
    """
    cursor.execute(query)
    return pd.DataFrame(
        cursor.fetchall(),
        columns=["warehouse_id", "city", "capacity", "origin_shipments", "destination_shipments", "traffic_count"],
    )
