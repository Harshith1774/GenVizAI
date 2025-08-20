import streamlit as st
import google.generativeai as genai

def configure_gemini():
    """
    Configures the Gemini API with the key from Streamlit secrets.
    Returns True on success, False on failure.
    """
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    except Exception:
        st.error("Error configuring Gemini API. Please make sure you have a valid GEMINI_API_KEY in your .streamlit/secrets.toml file.", icon="🚨")
        return False

@st.cache_data
def generate_sql_query(db_schema, db_dialect, question):
    """
    Generates a SQL query using the Gemini model based on the schema and user question.
    This function is cached to improve performance.
    """
    if not question:
        return None, "Please ask a question."

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert {db_dialect} query generator. Based on the database schema below, write a {db_dialect}-compatible SQL query to answer the user's question.
    Treat views as if they are regular tables. Only output the SQL query. 
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
