import configuration.DatabaseConnection as conn
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import numpy as np


def load_data(cursor,connection):
    print("-- Load the data --")
    
    courier_staff = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\courier_staff.csv")
    create_and_load_courier_staff(cursor,connection,courier_staff)

    shipments = pd.read_json(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\shipments.json")
    create_and_load_shipments(cursor,connection,shipments)

    shipment_tracking = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\shipment_tracking.csv")
    create_and_load_shipment_tracking(cursor,connection,shipment_tracking)

    routes = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\routes.csv")
    create_and_load_routes(cursor,connection,routes)

    warehouses = pd.read_json(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\warehouses.json")
    create_and_load_warehouses(cursor,connection,warehouses)

    costs = pd.read_csv(r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\resources\Logistics_dataset\costs.csv")
    create_and_load_costs(cursor,connection,costs)


def get_unique_shipment_status(cursor, connection):
    
    query = "SELECT DISTINCT status FROM shipments"
    cursor.execute(query)
    unique_status = [row[0] for row in cursor.fetchall()]
    print("Unique shipment statuses:", unique_status)
    return unique_status

def get_total_shipments(cursor, connection):
    query = "SELECT count(shipment_id) FROM shipments"
    cursor.execute(query)
    total_shipments = cursor.fetchone()[0]
    return total_shipments

def get_active_couriers(cursor, connection):
    query = "SELECT count(distinct courier_id) FROM shipments where status in ('Pending','In Transit')"
    cursor.execute(query)
    active_couriers = cursor.fetchone()[0]
    return active_couriers

def get_total_costs(cursor, connection):
    query = "select sum(fuel_cost),sum(labor_cost),sum(misc_cost) from costs"
    cursor.execute(query)

    row = cursor.fetchone()
    total_costs = sum(row) if row else 0

    return total_costs

def get_avg_delivery_time(cursor, connection):
    query = "SELECT avg(datediff(delivery_date, order_date)) FROM shipments WHERE delivery_date IS NOT NULL"
    cursor.execute(query)
    avg_delivery_time = cursor.fetchone()[0]
    return avg_delivery_time

def get_shipments_over_time(cursor, connection):
    query = "SELECT order_date, count(shipment_id) as shipment_count FROM shipments group by order_date order by order_date"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['order_date', 'shipment_count'])
    df.set_index('order_date', inplace=True)
    return df

def get_top_origins(cursor, connection):
    query = "SELECT origin, count(shipment_id) as shipment_count FROM shipments group by origin order by shipment_count desc limit 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['origin', 'shipment_count'])
    df_sorted = df.sort_values(by='shipment_count', ascending=False)
    #df_sorted.set_index('origin', inplace=True)
    return df_sorted

def get_top_destinations(cursor, connection):
    query = "SELECT destination, count(shipment_id) as shipment_count FROM shipments group by destination order by shipment_count desc limit 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['destination', 'shipment_count'])
    df_sorted = df.sort_values(by='shipment_count', ascending=False)
    #df_sorted.set_index('destination', inplace=True)
    return df_sorted

def get_shipment_tracking_details(cursor, connection, shipment_id):
    query = "SELECT status, timestamp FROM shipment_tracking WHERE shipment_id = %s order by timestamp"
    cursor.execute(query, (shipment_id,))
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['status', 'timestamp'])
    return df

def get_top_couriers(cursor, connection):
    query = " SELECT cs.name courier_name,cs.rating rating,cs.vehicle_type,count(ship.courier_id) total_deliveries FROM logistics.courier_staff cs,logistics.shipments ship where cs.courier_id = ship.courier_id " \
    "and ship.status = 'Delivered' group by cs.name,cs.rating,cs.vehicle_type order by total_deliveries desc,cs.rating desc limit 10"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['courier_name', 'rating', 'vehicle_type', 'total_deliveries'])
    return df

def get_courier_costs(cursor, connection):
    query = "select sum(fuel_cost) fuel_cost,sum(labor_cost) labor_cost,sum(misc_cost) misc_cost from costs"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['fuel_cost', 'labor_cost', 'misc_cost'])
    return df

def create_and_load_courier_staff(cursor, connection, courier_staff):
    
    query = """create table IF NOT EXISTS courier_staff (
    courier_id varchar(50) primary key ,
    name varchar(150), 
    rating Decimal(3,1) check(rating >= 1.0 AND rating <= 5.0),
    vehicle_type ENUM('Bike','Van','Truck', 'Car'))"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - courier_staff")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'courier_staff' already exists. Safely skipped.")
        else:
            # If it's a genuine syntax or connection error, raise it
            raise err
        
    
    print("-- Load the data ---courier_staff----")

    query = "insert IGNORE into courier_staff values (%s,%s,%s,%s)"

    cursor.executemany(query,courier_staff.values.tolist())
    connection.commit()
    print("Data inserted into courier_staff")

def create_and_load_shipments(cursor, connection, shipments):
    
    query = """create table IF NOT EXISTS shipments (
    shipment_id varchar(50) primary key ,
    order_date date not null, 
    origin varchar(100),
    destination varchar(100),
    weight Decimal(10,2),
    courier_id varchar(50),
    status varchar(50),
    delivery_date date null,
    foreign key(courier_id) references courier_staff (courier_id))"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - shipments")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'shipments' already exists")
        else:
            raise err
        
    
    print("-- Load the data ---shipments----")

    query = "insert IGNORE into shipments values (%s,%s,%s,%s,%s,%s,%s,%s)"
    shipments = shipments.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, shipments.values.tolist())
    connection.commit()
    print("Data inserted into shipments")

def create_and_load_shipment_tracking(cursor, connection, shipment_tracking):
    
    query = """create table IF NOT EXISTS shipment_tracking (
    tracking_id int primary key ,
    shipment_id varchar(50),
    status varchar(50),
    timestamp datetime,
    foreign key(shipment_id) references shipments (shipment_id))"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - shipment_tracking")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'shipment_tracking' already exists")
        else:
            raise err

    print("-- Load the data ---shipment_tracking----")

    query = "insert IGNORE into shipment_tracking values (%s,%s,%s,%s)"
    shipment_tracking = shipment_tracking.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, shipment_tracking.values.tolist())
    connection.commit()
    print("Data inserted into shipment_tracking")

def create_and_load_routes(cursor, connection, routes):
    
    query = """create table IF NOT EXISTS routes (
    route_id varchar(50) primary key ,
    origin varchar(100),
    destination varchar(100),
    distance_km decimal(10,2),
    avg_time_hours decimal(5,2))"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - routes")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'routes' already exists")
        else:
            raise err

    print("-- Load the data ---routes----")

    query = "insert IGNORE into routes values (%s,%s,%s,%s,%s)"
    routes = routes.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, routes.values.tolist())
    connection.commit()
    print("Data inserted into routes")

def create_and_load_warehouses(cursor, connection, warehouses):
    
    query = """create table IF NOT EXISTS warehouses (
    warehouse_id varchar(50) primary key ,
    city varchar(100),
    state varchar(50),
    capacity int)"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - warehouses")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'warehouses' already exists")
        else:
            raise err

    print("-- Load the data ---warehouses----")

    query = "insert IGNORE into warehouses values (%s,%s,%s,%s)"
    warehouses = warehouses.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, warehouses.values.tolist())
    connection.commit()
    print("Data inserted into warehouses")

def create_and_load_costs(cursor, connection, costs):
    
    query = """create table IF NOT EXISTS costs (
    shipment_id varchar(50) primary key ,
    fuel_cost decimal(15,2),
    labor_cost decimal(15,2),
    misc_cost decimal(15,2))"""


    try:
        #print(query)
        cursor.execute(query)
        connection.commit()
        print("Table ready - costs")

    except mysql.connector.Error as err:
        # 1050 corresponds to ER_TABLE_EXISTS_ERROR
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table 'costs' already exists")
        else:
            raise err

    print("-- Load the data ---costs----")

    query = "insert IGNORE into costs values (%s,%s,%s,%s)"
    costs = costs.replace({pd.NA: None, np.nan: None})
    cursor.executemany(query, costs.values.tolist())
    connection.commit()
    print("Data inserted into costs")
