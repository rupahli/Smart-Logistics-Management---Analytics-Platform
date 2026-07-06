import pandas as pd


def get_shipments_over_time(cursor, connection):
    query = "select order_date, count(shipment_id) as shipment_count from shipments group by order_date order by order_date"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["order_date", "shipment_count"])
    df.set_index("order_date", inplace=True)
    return df


def get_top_origins(cursor, connection):
    query = "select origin, count(shipment_id) as shipment_count from shipments group by origin order by shipment_count desc limit 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["origin", "shipment_count"])
    return df.sort_values(by="shipment_count", ascending=False)


def get_top_destinations(cursor, connection):
    query = "select destination, count(shipment_id) as shipment_count from shipments group by destination order by shipment_count desc limit 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["destination", "shipment_count"])
    return df.sort_values(by="shipment_count", ascending=False)


def get_shipment_tracking_details(cursor, connection, shipment_id):
    query = "select status, timestamp from shipment_tracking where shipment_id = %s order by timestamp"
    cursor.execute(query, (shipment_id,))
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["status", "timestamp"])


def get_top_couriers(cursor, connection):
    query = (
        "select cs.name courier_name, cs.rating rating, cs.vehicle_type, count(ship.courier_id) total_deliveries from logistics.courier_staff cs, logistics.shipments ship "
        "where cs.courier_id = ship.courier_id and ship.status = 'delivered' "
        "group by cs.name, cs.rating, cs.vehicle_type order by total_deliveries desc, cs.rating desc limit 10"
    )
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["courier_name", "rating", "vehicle_type", "total_deliveries"])


def get_courier_costs(cursor, connection):
    query = "select sum(fuel_cost) fuel_cost, sum(labor_cost) labor_cost, sum(misc_cost) misc_cost from costs"
    cursor.execute(query)
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["fuel_cost", "labor_cost", "misc_cost"])
