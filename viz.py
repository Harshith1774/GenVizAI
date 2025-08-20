import streamlit as st
import plotly.express as px
import pandas as pd

def create_smart_chart(df: pd.DataFrame):

    if df is None or df.empty:
        return None

    # Smart Date Conversion
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            pass

    # --- Rule 1: Metric Card for a single value ---
    if df.shape[0] == 1 and df.shape[1] == 1:
        st.metric("Result", df.iloc[0, 0])
        return "metric"

    numeric_cols = df.select_dtypes(include=['number']).columns
    string_cols = df.select_dtypes(include=['object', 'category']).columns
    date_cols = df.select_dtypes(include=['datetime64']).columns

    # --- Rule 2: Bar Chart ---
    if len(numeric_cols) == 1 and len(string_cols) >= 1:
        y_ax = numeric_cols[0]
        x_ax = df[string_cols].nunique().idxmax()
        fig = px.bar(df, x=x_ax, y=y_ax, title=f"{y_ax} by {x_ax}")
        return fig

    # --- Rule 3: Line Chart ---
    if len(date_cols) == 1 and len(numeric_cols) >= 1:
        x_ax = date_cols[0]
        y_axes = numeric_cols
        fig = px.line(df, x=x_ax, y=y_axes, title=f"{', '.join(y_axes)} over time")
        return fig
        
    # --- New Rule 4: Scatter Plot ---
    if len(numeric_cols) == 2:
        x_ax, y_ax = numeric_cols[0], numeric_cols[1]
        fig = px.scatter(df, x=x_ax, y=y_ax, title=f"{y_ax} vs. {x_ax}")
        return fig

    # --- New Rule 5: Pie Chart ---
    if len(numeric_cols) == 1 and len(string_cols) == 1:
        # Pie charts are good for a small number of categories
        if df[string_cols[0]].nunique() < 10:
            names_col = string_cols[0]
            values_col = numeric_cols[0]
            fig = px.pie(df, names=names_col, values=values_col, title=f"Distribution of {values_col} by {names_col}")
            return fig

    # --- Fallback: If no rules match ---
    return None
