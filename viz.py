import streamlit as st
import plotly.express as px
import pandas as pd

def create_smart_chart(df: pd.DataFrame):
    """
    Analyzes a DataFrame and creates the most appropriate Plotly chart.
    """
    if df is None or df.empty:
        return None

    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            pass

    if df.shape[0] == 1 and df.shape[1] == 1:
        st.metric("Result", df.iloc[0, 0])
        return "metric"

    numeric_cols = df.select_dtypes(include=['number']).columns
    string_cols = df.select_dtypes(include=['object', 'category']).columns
    date_cols = df.select_dtypes(include=['datetime64']).columns

    if len(numeric_cols) == 1 and len(string_cols) >= 1:
        y_ax = numeric_cols[0]
        x_ax = df[string_cols].nunique().idxmax()
        fig = px.bar(df, x=x_ax, y=y_ax, title=f"{y_ax} by {x_ax}")
        return fig

    if len(date_cols) == 1 and len(numeric_cols) >= 1:
        x_ax = date_cols[0]
        y_axes = numeric_cols
        fig = px.line(df, x=x_ax, y=y_axes, title=f"{', '.join(y_axes)} over time")
        return fig
        
    if len(numeric_cols) == 2:
        x_ax, y_ax = numeric_cols[0], numeric_cols[1]
        fig = px.scatter(df, x=x_ax, y=y_ax, title=f"{y_ax} vs. {x_ax}")
        return fig

    if len(numeric_cols) == 1 and len(string_cols) == 1:
        if df[string_cols[0]].nunique() < 10:
            names_col = string_cols[0]
            values_col = numeric_cols[0]
            fig = px.pie(df, names=names_col, values=values_col, title=f"Distribution of {values_col} by {names_col}")
            return fig

    return None
