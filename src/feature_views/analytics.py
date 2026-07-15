import streamlit as st
import plotly.express as px
import data.analytics_queries as analytics


def display_analytical_placeholder(option, cursor, connection):
    st.header(option)

    if option == "Delivery Performance Insights":
        
        metrics = analytics.get_delivery_performance_metrics(cursor, connection)
        st.subheader("Average delivery time per route")
        st.dataframe(metrics["delivery_summary"], use_container_width=True)

        st.subheader("Most delayed routes")
        st.dataframe(metrics["delayed_routes"], use_container_width=True)

        st.subheader("Delivery time vs distance comparison")
        fig = px.line(
            metrics["distance_comparison"],
            x="distance_km",
            y="avg_delivery_days",
            #size="shipment_count" if "shipment_count" in metrics["distance_comparison"].columns else None,
            #hover_name="origin",
            #text="destination",
            title="Delivery Time vs Distance",
        )
        st.plotly_chart(fig, width="stretch")

        
        fig = px.scatter(
            metrics["distance_comparison"],
            x="distance_km",
            y="avg_delivery_days",
            color='origin', color_continuous_scale='Viridis', 
            title="Delivery Time vs Distance Based on origin",
        )
        st.plotly_chart(fig, width="stretch")

        fig = px.scatter(
            metrics["distance_comparison"],
            x="distance_km",
            y="avg_delivery_days",
            color='destination', color_continuous_scale='Viridis', 
            title="Delivery Time vs Distance Based on destination",
        )
        st.plotly_chart(fig, width="stretch")

    elif option == "Courier Performance":
        
        courier_metrics = analytics.get_courier_performance_metrics(cursor, connection)
        st.subheader("Shipments handled per courier")
        st.dataframe(courier_metrics, use_container_width=True)

        st.subheader("On-time delivery %")
        
        #st.bar_chart(courier_metrics.set_index("name")["on_time_pct"].head(10))

        
        #st.bar_chart(courier_metrics.set_index("name")["avg_rating"].head(10))
        
        df_sorted = courier_metrics.sort_values(by='on_time_pct', ascending=False).head(40)
        
        fig = px.bar(x=df_sorted["name"], y=df_sorted["on_time_pct"])
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(range=[30, 50])
        st.plotly_chart(fig, width="stretch")

        df_sorted_avg_rating = courier_metrics.sort_values(by='avg_rating', ascending=False)
        st.subheader("Average rating comparison")
        fig = px.bar(x=df_sorted_avg_rating["name"], y=df_sorted_avg_rating["avg_rating"])
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(range=[3, 6])
        st.plotly_chart(fig, width="stretch")


        


    elif option == "Cost Analytics":
        
        cost_metrics = analytics.get_cost_analytics_metrics(cursor, connection)
        st.subheader("Total cost per shipment")
        st.dataframe(cost_metrics["cost_per_shipment"], use_container_width=True)

        st.subheader("Cost per route")
        st.dataframe(cost_metrics["cost_per_route"], use_container_width=True)

        st.subheader("Fuel vs labor percentage contribution")
        st.dataframe(cost_metrics["cost_mix"], use_container_width=True)

        st.subheader("High-cost shipments")
        st.dataframe(cost_metrics["high_cost_shipments"], use_container_width=True)

    elif option == "Cancellation Analysis":
        
        cancellation_metrics = analytics.get_cancellation_analysis_metrics(cursor, connection)
        st.subheader("Cancellation rate by origin")
        st.dataframe(cancellation_metrics["cancellation_by_origin"], use_container_width=True)

        st.subheader("Cancellation rate by courier")
        st.dataframe(cancellation_metrics["cancellation_by_courier"], use_container_width=True)

        st.subheader("Time-to-cancellation analysis")
        st.dataframe(cancellation_metrics["time_to_cancellation"], use_container_width=True)

    elif option == "Warehouse Insights":
        
        warehouse_metrics = analytics.get_warehouse_insights_metrics(cursor, connection)
        st.subheader("Warehouse capacity comparison")
        st.dataframe(warehouse_metrics, use_container_width=True)

        st.subheader("High-traffic warehouse cities")
        #st.bar_chart(warehouse_metrics.set_index("city")["traffic_count"])


        fig = px.bar(warehouse_metrics,x="city", y="traffic_count",color_continuous_scale=px.colors.sequential.Viridis)
        fig.update_xaxes(tickangle=45)
        #fig.update_yaxes(range=[30, 50])
        st.plotly_chart(fig, width="stretch")


    else:
        st.info("Select an analytical view from the sidebar.")
