import pandas as pd


def get_shipment_filters(cursor, connection):
    cursor.execute("SELECT DISTINCT status FROM shipments WHERE status IS NOT NULL ORDER BY status")
    statuses = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT origin FROM shipments WHERE origin IS NOT NULL ORDER BY origin")
    origins = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT destination FROM shipments WHERE destination IS NOT NULL ORDER BY destination")
    destinations = [row[0] for row in cursor.fetchall()]

    return statuses, origins, destinations


def get_filtered_shipments(cursor, connection, filters):
    query = "SELECT shipment_id, order_date, origin, destination, status, courier_id, delivery_date FROM shipments WHERE 1=1"
    params = []

    if filters.get("shipment_id", "").strip():
        query += " AND shipment_id = %s"
        params.append(filters["shipment_id"].strip())

    if filters.get("status") not in (None, "All"):
        query += " AND status = %s"
        params.append(filters["status"])

    if filters.get("origin") not in (None, "All"):
        query += " AND origin = %s"
        params.append(filters["origin"])

    if filters.get("destination") not in (None, "All"):
        query += " AND destination = %s"
        params.append(filters["destination"])

    if filters.get("start_date") and filters.get("end_date"):
        query += " AND order_date BETWEEN %s AND %s"
        params.extend([filters["start_date"], filters["end_date"]])

    query += " ORDER BY order_date DESC LIMIT 100"

    cursor.execute(query, params)
    shipment_rows = cursor.fetchall()

    return pd.DataFrame(
        shipment_rows,
        columns=["shipment_id", "order_date", "origin", "destination", "status", "courier_id", "delivery_date"],
    )
