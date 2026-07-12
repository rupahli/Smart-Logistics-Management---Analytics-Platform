# Smart Logistics Management & Analytics Platform

## Project Overview
This project is a Streamlit-based logistics dashboard that helps users explore shipment data, search and filter shipments, track operational performance, and view analytical insights for logistics operations.

## Tech Stack
- Python
- Streamlit
- MySQL
- Pandas
- NumPy
- JSON / CSV data processing

## Project Structure
- src/LogisticsAnalysis.py - main app entry point
- src/feature_views/ - dashboard pages for home, shipment search, KPIs, and analytics
- src/data/ - query and data-loading modules
- resources/Logistics_dataset/ - sample logistics datasets

## Run the Project
1. Activate your Python environment
   ```bash
   .\.logistic\Scripts\Activate.ps1
   ```
2. Install required packages
   ```bash
   pip install streamlit pandas mysql-connector-python numpy
   ```
3. Start the app
   ```bash
   streamlit run src/LogisticsAnalysis.py
   ```

## Features
- Shipment search and filtering
- Operational KPI views
- Analytical insights for logistics performance

