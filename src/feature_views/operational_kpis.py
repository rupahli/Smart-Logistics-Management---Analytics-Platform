import streamlit as st
import data.operational_queries as operational_queries


def display_operational_kpis(cursor, connection):
    st.header("Operational KPIs")
    
    data = operational_queries.get_operational_kpi_metrics(cursor, connection)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Shipments", f"{data[0]}")
    col2.metric("Delivered Shipments %", f"{data[1]}%")
    col3.metric("Cancelled Shipments %", f"{data[2]}%")
    col4.metric("Average Delivery Time", f"{data[3]:.2f} days")
    col5.metric("Total Operational Cost", f"${data[4]}")
