import pandas as pd


def get_shipment_filters(cursor, connection):
    cursor.execute("select distinct status from shipments where status is not null order by status")
    statuses = [row[0] for row in cursor.fetchall()]

    cursor.execute("select distinct origin from shipments where origin is not null order by origin")
    origins = [row[0] for row in cursor.fetchall()]

    cursor.execute("select distinct destination from shipments where destination is not null order by destination")
    destinations = [row[0] for row in cursor.fetchall()]

    return statuses, origins, destinations


def get_filtered_shipments(cursor, connection, filters):
    query = "select shipment_id, order_date, origin, destination, status, courier_id, delivery_date from shipments where 1=1"
    params = []

    if filters.get("shipment_id", "").strip():
        query += " and shipment_id = %s"
        params.append(filters["shipment_id"].strip())

    if filters.get("status") not in (None, "All"):
        query += " and status = %s"
        params.append(filters["status"])

    if filters.get("origin") not in (None, "All"):
        query += " and origin = %s"
        params.append(filters["origin"])

    if filters.get("destination") not in (None, "All"):
        query += " and destination = %s"
        params.append(filters["destination"])

    if filters.get("start_date") and filters.get("end_date"):
        query += " and order_date between %s and %s"
        params.extend([filters["start_date"], filters["end_date"]])

    query += " order by order_date desc"

    cursor.execute(query, params)
    shipment_rows = cursor.fetchall()

    return pd.DataFrame(
        shipment_rows,
        columns=["shipment_id", "order_date", "origin", "destination", "status", "courier_id", "delivery_date"],
    )
