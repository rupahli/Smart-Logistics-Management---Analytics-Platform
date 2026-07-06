from data.common_datasetload import get_total_shipments, get_delivered_shipments_count, get_cancelled_shipments_count, get_avg_delivery_time, get_total_costs

def get_operational_kpi_metrics(cursor, connection):
    
    total_shipments = get_total_shipments(cursor, connection)
    delivered_shipments = get_delivered_shipments_count(cursor, connection)
    cancelled_shipments = get_cancelled_shipments_count(cursor, connection)
    avg_delivery_time = get_avg_delivery_time(cursor, connection)
    total_costs = get_total_costs(cursor, connection)

    delivered_pct = round((delivered_shipments / total_shipments * 100) , 2)
    cancelled_pct = round((cancelled_shipments / total_shipments * 100) , 2)

    return total_shipments, delivered_pct, cancelled_pct, avg_delivery_time, total_costs
