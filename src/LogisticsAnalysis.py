import streamlit as st
import configuration.DatabaseConnection as conn
from data.common_datasetload import load_data
from feature_views.home import display_home_page
from feature_views.shipment_search import display_shipment_search_and_filtering
from feature_views.operational_kpis import display_operational_kpis
from feature_views.analytics import display_analytical_placeholder


def main():
    print("-- Start the Management and Analytics Platform --")

    st.set_page_config(layout="wide")

    if "cursor" not in st.session_state or "connection" not in st.session_state:
        cursor, connection = conn.load_connection()
        load_data(cursor, connection)
        st.session_state.cursor = cursor
        st.session_state.connection = connection
    else:
        cursor = st.session_state.cursor
        connection = st.session_state.connection

    st.sidebar.title("Navigation")
    st.sidebar.caption("Smart Logistics Management & Analytics Platform")

    main_option = st.sidebar.radio(
        "Choose a feature to view",
        [
            "Home",
            "Shipment Search & Filtering",
            "Operational KPIs",
            "Analytical Views",
        ],
        index=0,
    )

    if main_option == "Home":
        display_home_page(cursor, connection)
    elif main_option == "Shipment Search & Filtering":
        display_shipment_search_and_filtering(cursor, connection)
    elif main_option == "Operational KPIs":
        display_operational_kpis(cursor, connection)
    else:
        analytical_option = st.sidebar.radio(
            "Analytical Views",
            [
                "Delivery Performance Insights",
                "Courier Performance",
                "Cost Analytics",
                "Cancellation Analysis",
                "Warehouse Insights",
            ],
            index=0,
        )
        display_analytical_placeholder(analytical_option, cursor, connection)


if __name__ == "__main__":
    main()
