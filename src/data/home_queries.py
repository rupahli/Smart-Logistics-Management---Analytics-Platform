import pandas as pd


def get_shipments_over_time(cursor, connection):
    query = "SELECT order_date, COUNT(shipment_id) AS shipment_count FROM shipments GROUP BY order_date ORDER BY order_date"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["order_date", "shipment_count"])
    df.set_index("order_date", inplace=True)
    return df


def get_top_origins(cursor, connection):
    query = "SELECT origin, COUNT(shipment_id) AS shipment_count FROM shipments GROUP BY origin ORDER BY shipment_count DESC LIMIT 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["origin", "shipment_count"])
    return df.sort_values(by="shipment_count", ascending=False)


def get_top_destinations(cursor, connection):
    query = "SELECT destination, COUNT(shipment_id) AS shipment_count FROM shipments GROUP BY destination ORDER BY shipment_count DESC LIMIT 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["destination", "shipment_count"])
    return df.sort_values(by="shipment_count", ascending=False)


def get_shipment_tracking_details(cursor, connection, shipment_id):
    query = "SELECT status, timestamp FROM shipment_tracking WHERE shipment_id = %s ORDER BY timestamp"
    cursor.execute(query, (shipment_id,))
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["status", "timestamp"])


def get_top_couriers(cursor, connection):
    query = (
        "SELECT cs.name courier_name, cs.rating rating, cs.vehicle_type, COUNT(ship.courier_id) total_deliveries "
        "FROM logistics.courier_staff cs, logistics.shipments ship "
        "WHERE cs.courier_id = ship.courier_id AND ship.status = 'Delivered' "
        "GROUP BY cs.name, cs.rating, cs.vehicle_type "
        "ORDER BY total_deliveries DESC, cs.rating DESC LIMIT 10"
    )
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["courier_name", "rating", "vehicle_type", "total_deliveries"])


def get_courier_costs(cursor, connection):
    query = "SELECT SUM(fuel_cost) fuel_cost, SUM(labor_cost) labor_cost, SUM(misc_cost) misc_cost FROM costs"
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["fuel_cost", "labor_cost", "misc_cost"])
