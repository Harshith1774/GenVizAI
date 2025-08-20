import streamlit as st
import google.generativeai as genai

def configure_gemini(api_key):
    """
    Configures the Gemini API with the provided key.
    Returns True on success, False on failure.
    """
    if not api_key:
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}", icon="🚨")
        return False

@st.cache_data
def generate_sql_query(db_schema, db_dialect, db_version, question):
    """
    Generates a SQL query using the Gemini model based on the schema, version, and user question.
    """
    if not question:
        return None, "Please ask a question."

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert SQL query generator. Your task is to write a query compatible with a specific database version.

    Database Type: {db_dialect}
    Database Version: {db_version}

    Based on the database schema below, write a {db_dialect}-compatible SQL query to answer the user's question.
    Only output the SQL query. 
    
    If you cannot answer the question with the given schema, explain why in SQL comments.

    {db_schema}

    **Question:**
    {question}

    **SQL Query:**
    """
    
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip().replace("```sql", "").replace("```", "")
        return sql_query, None
    except Exception as e:
        return None, f"Error generating SQL query: {e}"
