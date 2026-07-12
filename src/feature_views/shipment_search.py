import streamlit as st
import pandas as pd
import data.shipment_queries as shipment_queries


def display_shipment_search_and_filtering(cursor, connection):
    st.header("Shipment Search & Filtering")
    
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

    col4, col5 = st.columns(2)
    with col4:
        start_date = st.date_input(
            "Start date",
            value=None,
            format="YYYY-MM-DD",
        )
    with col5:
        end_date = st.date_input(
            "End date",
            value=None,
            format="YYYY-MM-DD",
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        st.warning("Start date cannot be after end date.")

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
