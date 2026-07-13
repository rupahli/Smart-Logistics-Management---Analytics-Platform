import pandas as pd


def get_delivery_performance_metrics(cursor, connection):
    query = """
        select s.origin, s.destination,
               round(avg(datediff(s.delivery_date, s.order_date)), 2) as avg_delivery_days,
               count(s.shipment_id) as shipment_count
        from shipments s
        left join routes r on s.origin = r.origin and s.destination = r.destination
        where s.delivery_date is not null and s.order_date is not null
        group by s.origin, s.destination
        order by avg_delivery_days desc
    """
    cursor.execute(query)
    delivery_summary = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "avg_delivery_days", "shipment_count"],
    )

    delayed_query = """
        select s.origin, s.destination,
               round(avg(datediff(s.delivery_date, s.order_date) - (r.avg_time_hours / 24)), 2) as delay_days,
               count(s.shipment_id) as shipment_count
        from shipments s
        left join routes r on s.origin = r.origin and s.destination = r.destination
        where s.delivery_date is not null and s.order_date is not null
        group by s.origin, s.destination
        order by delay_days desc
    """
    cursor.execute(delayed_query)
    delayed_routes = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "delay_days", "shipment_count"],
    )

    comparison_query = """
        select s.origin, s.destination,
               round(avg(datediff(s.delivery_date, s.order_date)), 2) as avg_delivery_days,
               round(avg(r.distance_km), 2) as distance_km
        from shipments s
        left join routes r on s.origin = r.origin and s.destination = r.destination
        where s.delivery_date is not null and s.order_date is not null
        group by s.origin, s.destination
        order by distance_km desc
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
        select s.courier_id, cs.name,
               count(s.shipment_id) as shipments_handled,
               round(100.0 * sum(case when s.status = 'Delivered' then 1 else 0 end) / count(s.shipment_id), 2) as on_time_pct,
               round(avg(cs.rating), 1) as avg_rating
        from shipments s
        left join courier_staff cs on s.courier_id = cs.courier_id
        group by s.courier_id, cs.name
        order by shipments_handled desc
    """
    cursor.execute(query)
    return pd.DataFrame(
        cursor.fetchall(),
        columns=["courier_id", "name", "shipments_handled", "on_time_pct", "avg_rating"],
    )


def get_cost_analytics_metrics(cursor, connection):
    total_cost_query = """
        select s.shipment_id, s.origin, s.destination,
               round((c.fuel_cost + c.labor_cost + c.misc_cost), 2) as total_cost,
               round((c.fuel_cost), 2) as fuel_cost,
               round((c.labor_cost), 2) as labor_cost,
               round((c.misc_cost), 2) as misc_cost
        from shipments s
        left join costs c on s.shipment_id = c.shipment_id
        order by total_cost desc
    """
    cursor.execute(total_cost_query)
    cost_per_shipment = pd.DataFrame(
        cursor.fetchall(),
        columns=["shipment_id", "origin", "destination", "total_cost", "fuel_cost", "labor_cost", "misc_cost"],
    )

    route_cost_query = """
        select s.origin, s.destination,
               round(sum(c.fuel_cost + c.labor_cost + c.misc_cost), 2) as route_cost,
               count(s.shipment_id) as shipment_count
        from shipments s
        left join costs c on s.shipment_id = c.shipment_id
        group by s.origin, s.destination
        order by route_cost desc
    """
    cursor.execute(route_cost_query)
    cost_per_route = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "destination", "route_cost", "shipment_count"],
    )

    cost_mix_query = """
        select round((sum(c.fuel_cost) / sum(c.fuel_cost + c.labor_cost + c.misc_cost)) * 100, 2) as fuel_pct,
               round((sum(c.labor_cost) / sum(c.fuel_cost + c.labor_cost + c.misc_cost)) * 100, 2) as labor_pct
        from costs c
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
        select s.origin,
               round(100.0 * sum(case when s.status = 'Cancelled' then 1 else 0 end) / count(s.shipment_id), 2) as cancellation_rate,
               count(s.shipment_id) as shipment_count
        from shipments s
        group by s.origin
        order by cancellation_rate desc
    """
    cursor.execute(origin_query)
    cancellation_by_origin = pd.DataFrame(
        cursor.fetchall(),
        columns=["origin", "cancellation_rate", "shipment_count"],
    )

    courier_query = """
        select s.courier_id, cs.name,
               round(100.0 * sum(case when s.status = 'Cancelled' then 1 else 0 end) / count(s.shipment_id), 2) as cancellation_rate,
               count(s.shipment_id) as shipment_count
        from shipments s
        left join courier_staff cs on s.courier_id = cs.courier_id
        group by s.courier_id, cs.name
        order by cancellation_rate desc
    """
    cursor.execute(courier_query)
    cancellation_by_courier = pd.DataFrame(
        cursor.fetchall(),
        columns=["courier_id", "name", "cancellation_rate", "shipment_count"],
    )

    time_query = """
        select s.shipment_id, s.origin, s.destination, s.order_date,
               min(st.timestamp) as cancellation_time,
               datediff(min(st.timestamp), s.order_date) as days_to_cancel
        from shipments s
        join shipment_tracking st on s.shipment_id = st.shipment_id
        where st.status = 'Cancelled'
        group by s.shipment_id, s.origin, s.destination, s.order_date
        order by days_to_cancel desc
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
        select w.warehouse_id, w.city, w.capacity,
               sum(case when s.origin = w.city then 1 else 0 end) as origin_shipments,
               sum(case when s.destination = w.city then 1 else 0 end) as destination_shipments,
               sum(case when s.origin = w.city then 1 else 0 end) + sum(case when s.destination = w.city then 1 else 0 end) as traffic_count
        from warehouses w
        left join shipments s on s.origin = w.city or s.destination = w.city
        group by w.warehouse_id, w.city, w.capacity
        order by traffic_count desc
    """
    cursor.execute(query)
    return pd.DataFrame(
        cursor.fetchall(),
        columns=["warehouse_id", "city", "capacity", "origin_shipments", "destination_shipments", "traffic_count"],
    )
