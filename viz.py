import streamlit as st
import plotly.express as px
import pandas as pd

def create_smart_chart(df: pd.DataFrame):
    """
    Analyzes a DataFrame and creates the most appropriate Plotly chart.
    Returns a Plotly figure object or None if no suitable chart can be created.
    """
    if df is None or df.empty:
        return None

    # --- New: Smart Date Conversion ---
    # Attempt to convert any object columns that look like dates into datetime objects
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            # This column is not a date, so we leave it as is
            pass
    # --- End of New Code ---

    # --- Rule 1: Metric Card for a single value ---
    if df.shape[0] == 1 and df.shape[1] == 1:
        # Create a metric card using st.metric
        st.metric("Result", df.iloc[0, 0])
        return "metric" # Special return type for metric

    # --- Rule 2: Bar Chart for categorical data ---
    # Identifies one text column and one numeric column
    numeric_cols = df.select_dtypes(include=['number']).columns
    string_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(numeric_cols) == 1 and len(string_cols) == 1:
        x_ax = string_cols[0]
        y_ax = numeric_cols[0]
        fig = px.bar(df, x=x_ax, y=y_ax, title=f"{y_ax} by {x_ax}")
        return fig

    # --- Rule 3: Line Chart for time-series data ---
    # This rule will now work thanks to the smart conversion above
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) == 1 and len(numeric_cols) >= 1:
        # Allow one date column and one or more numeric columns
        x_ax = date_cols[0]
        y_axes = numeric_cols
        fig = px.line(df, x=x_ax, y=y_axes, title=f"{', '.join(y_axes)} over time")
        return fig
        
    # --- Fallback: If no rules match, don't create a chart ---
    return None
