import streamlit as st
import plotly.express as px
import pandas as pd
import data.common_datasetload as common_data
import data.home_queries as home_queries


def display_home_page(cursor, connection):
    display_Title()
    display_overalll_kpis(cursor, connection)
    display_shipment_trends(cursor, connection)
    display_GeoSpatial_analysis(cursor, connection)
    display_realtime_shipment_tracking(cursor, connection)
    display_coruier_performance(cursor, connection)


def display_Title():
    st.title("Smart Logistics Management & Analytics Platform")
    st.subheader("Detailed analysis of the logistics data in real time")


def display_overalll_kpis(cursor, connection):
    st.header("Overview KPIs")

    total_shipments = common_data.get_total_shipments(cursor, connection)
    active_couriers = common_data.get_active_couriers(cursor, connection)
    total_costs = common_data.get_total_costs(cursor, connection)
    avg_delivery_time = common_data.get_avg_delivery_time(cursor, connection)

    st.subheader("Overall KPIs")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", f"{total_shipments}")
    col2.metric("Active Couriers", f"{active_couriers}")
    col3.metric("Total Costs ($)", f"{total_costs}")
    col4.metric("Avg Delivery time in days", f"{avg_delivery_time}")


def display_shipment_trends(cursor, connection):
    st.header("Shipment Trends")
    st.subheader("Shipments over time")
    shipment_over_time = home_queries.get_shipments_over_time(cursor, connection)
    st.line_chart(shipment_over_time)


def display_GeoSpatial_analysis(cursor, connection):
    st.header("GeoSpatial Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 origins")
        top_origins = home_queries.get_top_origins(cursor, connection)
        fig = px.bar(
            top_origins,
            x="origin",
            y="shipment_count",
            title="Top Origins by Shipment Count",
            color="shipment_count",
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        st.plotly_chart(fig)

    with col2:
        st.subheader("Top 10 destinations")
        top_destinations = home_queries.get_top_destinations(cursor, connection)
        fig = px.bar(
            top_destinations,
            x="destination",
            y="shipment_count",
            title="Top Destinations by Shipment Count",
            color="shipment_count",
            color_continuous_scale=px.colors.sequential.Inferno,
        )
        st.plotly_chart(fig, width="stretch")


def display_realtime_shipment_tracking(cursor, connection):
    st.header("Real-time Shipment Tracking")
    shipment_id = st.text_input("Enter Shipment ID to track").strip()

    if shipment_id:
        tracking_details = home_queries.get_shipment_tracking_details(cursor, connection, shipment_id)
        if not tracking_details.empty:
            st.dataframe(tracking_details)
        else:
            st.warning("No tracking details found for this shipment ID.")


def display_coruier_performance(cursor, connection):
    st.header("Courier Performance Section")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 performing couriers")
        st.write("Ranked by most shipments delivered successfully")
        top_couriers = home_queries.get_top_couriers(cursor, connection)
        st.dataframe(top_couriers)

    with col2:
        st.subheader("Financial Breakdown of Courier costs")
        courier_costs = home_queries.get_courier_costs(cursor, connection)

        costs_data = {
            "Cost Type": ["Fuel Cost", "Labor Cost", "Misc Cost"],
            "Amount": [
                courier_costs["fuel_cost"].iloc[0],
                courier_costs["labor_cost"].iloc[0],
                courier_costs["misc_cost"].iloc[0],
            ],
        }
        df_costs = pd.DataFrame(costs_data)

        fig = px.pie(
            df_costs,
            values="Amount",
            names="Cost Type",
            title="Distribution of Courier Costs",
        )
        st.plotly_chart(fig, width="stretch")
