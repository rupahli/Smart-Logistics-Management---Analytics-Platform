import DataSetLoad as dataSet
import streamlit as st
import configuration.DatabaseConnection as conn

def main():
    print("-- Start the Management and Analytics Platform --")

    cursor,connection = conn.load_connection()

    #dataSet.load_data(cursor,connection)

    display_Title()
    display_overalll_kpis(cursor,connection)
    display_shipment_trends(cursor,connection)


    search_id = st.text_input("Search by Shipment ID").strip()
    all_statuses = dataSet.get_unique_shipment_status(cursor,connection)

    selected_statuses = st.multiselect("Status", options=all_statuses, default=all_statuses)

def display_Title():
    st.title("Smart Logistics Management & Analytics Platform")
    st.subheader("Detailed analysis of the logistics data in real time")


def display_overalll_kpis(cursor,connection):
    
    st.header("Overview KPIs")
    
    total_shipments = dataSet.get_total_shipments(cursor,connection)
    active_couriers = dataSet.get_active_couriers(cursor,connection)
    total_costs = dataSet.get_total_costs(cursor,connection)
    avg_delivery_time = dataSet.get_avg_delivery_time(cursor,connection)

    st.subheader("Overall KPIs")
    col1, col2,col3,col4 = st.columns(4)
    col1.metric("Total Shipments", f"{total_shipments}")
    col2.metric("Active Couriers", f"{active_couriers}")
    col3.metric("Total Costs ($)", f"{total_costs}")
    col4.metric("Avg Delivery time in days", f"{avg_delivery_time}")

def display_overalll_kpis(cursor,connection):

    

if __name__ == "__main__":
    main()
