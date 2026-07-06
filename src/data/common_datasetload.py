import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import numpy as np


def load_data(cursor, connection):
    print("-- Load the data --")

    courier_staff = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\courier_staff.csv"
    )
    create_and_load_courier_staff(cursor, connection, courier_staff)

    shipments = pd.read_json(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\shipments.json"
    )
    create_and_load_shipments(cursor, connection, shipments)

    shipment_tracking = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\shipment_tracking.csv"
    )
    create_and_load_shipment_tracking(cursor, connection, shipment_tracking)

    routes = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\routes.csv"
    )
    create_and_load_routes(cursor, connection, routes)

    warehouses = pd.read_json(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\warehouses.json"
    )
    create_and_load_warehouses(cursor, connection, warehouses)

    costs = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\costs.csv"
    )
    create_and_load_costs(cursor, connection, costs)


def get_unique_shipment_status(cursor, connection):
    query = "SELECT DISTINCT status FROM shipments"
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def get_total_shipments(cursor, connection):
    query = "SELECT COUNT(shipment_id) FROM shipments"
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_active_couriers(cursor, connection):
    query = "SELECT COUNT(DISTINCT courier_id) FROM shipments WHERE status IN ('Pending', 'In Transit')"
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_total_costs(cursor, connection):
    query = "SELECT SUM(fuel_cost), SUM(labor_cost), SUM(misc_cost) FROM costs"
    cursor.execute(query)
    row = cursor.fetchone()

    sumval = 0 

    for x in row:
        sumval+=x

    return sumval


def get_avg_delivery_time(cursor, connection):
    query = "SELECT AVG(DATEDIFF(delivery_date, order_date)) FROM shipments WHERE delivery_date IS NOT NULL"
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_delivered_shipments_count(cursor, connection):
    query = "SELECT COUNT(*) FROM shipments WHERE status = 'Delivered'"
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_cancelled_shipments_count(cursor, connection):
    query = "SELECT COUNT(*) FROM shipments WHERE status = 'Cancelled'"
    cursor.execute(query)
    return cursor.fetchone()[0]


def create_and_load_courier_staff(cursor, connection, courier_staff):
    query = """CREATE TABLE IF NOT EXISTS courier_staff (
    courier_id varchar(50) primary key,
    name varchar(150),
    rating Decimal(3,1) check(rating >= 1.0 AND rating <= 5.0),
    vehicle_type ENUM('Bike','Van','Truck','Car'))"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - courier_staff")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'courier_staff' already exists. Safely skipped.")
        else:
            raise err

    query = "INSERT IGNORE INTO courier_staff VALUES (%s,%s,%s,%s)"
    cursor.executemany(query, courier_staff.values.tolist())
    connection.commit()
    print("Data inserted into courier_staff")


def create_and_load_shipments(cursor, connection, shipments):
    query = """CREATE TABLE IF NOT EXISTS shipments (
    shipment_id varchar(50) primary key,
    order_date date not null,
    origin varchar(100),
    destination varchar(100),
    weight Decimal(10,2),
    courier_id varchar(50),
    status varchar(50),
    delivery_date date null,
    foreign key(courier_id) references courier_staff (courier_id))"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - shipments")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'shipments' already exists")
        else:
            raise err

    query = "INSERT IGNORE INTO shipments VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    shipments = shipments.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, shipments.values.tolist())
    connection.commit()
    print("Data inserted into shipments")


def create_and_load_shipment_tracking(cursor, connection, shipment_tracking):
    query = """CREATE TABLE IF NOT EXISTS shipment_tracking (
    tracking_id int primary key,
    shipment_id varchar(50),
    status varchar(50),
    timestamp datetime,
    foreign key(shipment_id) references shipments (shipment_id))"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - shipment_tracking")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'shipment_tracking' already exists")
        else:
            raise err

    query = "INSERT IGNORE INTO shipment_tracking VALUES (%s,%s,%s,%s)"
    shipment_tracking = shipment_tracking.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, shipment_tracking.values.tolist())
    connection.commit()
    print("Data inserted into shipment_tracking")


def create_and_load_routes(cursor, connection, routes):
    query = """CREATE TABLE IF NOT EXISTS routes (
    route_id varchar(50) primary key,
    origin varchar(100),
    destination varchar(100),
    distance_km decimal(10,2),
    avg_time_hours decimal(5,2))"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - routes")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'routes' already exists")
        else:
            raise err

    query = "INSERT IGNORE INTO routes VALUES (%s,%s,%s,%s,%s)"
    routes = routes.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, routes.values.tolist())
    connection.commit()
    print("Data inserted into routes")


def create_and_load_warehouses(cursor, connection, warehouses):
    query = """CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id varchar(50) primary key,
    city varchar(100),
    state varchar(50),
    capacity int)"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - warehouses")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'warehouses' already exists")
        else:
            raise err

    query = "INSERT IGNORE INTO warehouses VALUES (%s,%s,%s,%s)"
    warehouses = warehouses.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, warehouses.values.tolist())
    connection.commit()
    print("Data inserted into warehouses")


def create_and_load_costs(cursor, connection, costs):
    query = """CREATE TABLE IF NOT EXISTS costs (
    shipment_id varchar(50) primary key,
    fuel_cost decimal(15,2),
    labor_cost decimal(15,2),
    misc_cost decimal(15,2))"""

    try:
        cursor.execute(query)
        connection.commit()
        print("Table ready - costs")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'costs' already exists")
        else:
            raise err

    query = "INSERT IGNORE INTO costs VALUES (%s,%s,%s,%s)"
    costs = costs.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, costs.values.tolist())
    connection.commit()
    print("Data inserted into costs")
