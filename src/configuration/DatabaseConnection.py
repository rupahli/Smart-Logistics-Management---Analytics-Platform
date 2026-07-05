import pandas as pd
import mysql.connector
import json



def load_connection():
    with open (r"C:\Users\KITTU-PALKIN\OneDrive\Documents\Rupahli\GUVI\Projects\Smart Logistics Management & Analytics Platform\src\configuration\connection.json",mode="r+") as tf:
        config=  json.load(tf)

    connection = mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database']

    )

    cursor = connection.cursor()
    query = "use Logistics"

    cursor.execute(query)

    return cursor,connection





