import streamlit as st
import pandas as pd
import data.shipment_queries as shipment_queries


def display_shipment_search_and_filtering(cursor, connection):
    st.header("Shipment Search & Filtering")
    st.markdown("- Search by shipment_id")
    st.markdown("- Filter by: status, origin, destination, and order date")

    shipment_id = st.text_input("Search by shipment_id", placeholder="Enter shipment ID")

    statuses, origins, destinations = shipment_queries.get_shipment_filters(cursor, connection)
    status_options = ["All"] + statuses
    origin_options = ["All"] + origins
    destination_options = ["All"] + destinations

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_status = st.selectbox("Filter by status", status_options)
    with col2:
        selected_origin = st.selectbox("Filter by origin", origin_options)
    with col3:
        selected_destination = st.selectbox("Filter by destination", destination_options)

    start_date, end_date = st.date_input(
        "Filter by order date range",
        value=(pd.Timestamp.today() - pd.Timedelta(days=30), pd.Timestamp.today()),
        format="YYYY-MM-DD",
    )

    if isinstance(start_date, tuple):
        start_date, end_date = start_date

    shipment_df = shipment_queries.get_filtered_shipments(
        cursor,
        connection,
        {
            "shipment_id": shipment_id,
            "status": selected_status,
            "origin": selected_origin,
            "destination": selected_destination,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    if not shipment_df.empty:
        st.subheader("Matching shipments")
        st.dataframe(shipment_df, use_container_width=True)
    else:
        st.info("No shipments matched the current search criteria.")
