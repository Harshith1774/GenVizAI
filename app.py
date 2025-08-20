import streamlit as st
import pandas as pd
from audiorecorder import audiorecorder

# Import utility functions from our other files
from database import create_db_engine, get_db_schema, get_db_version
from llm import configure_gemini, generate_sql_query
from speech import transcribe_audio
from viz import create_smart_chart

# --- Page Configuration ---
st.set_page_config(
    page_title="Genviz AI",
    page_icon="🤖",
    layout="wide"
)

# --- Main Application ---
def main():
    st.title("Genviz AI 🤖")

    # --- Sidebar ---
    with st.sidebar:
        st.header("1. Configuration")
        api_key = st.text_input("Gemini API Key", type="password")

        st.header("2. Database Connection")
        db_type = st.selectbox("Database Type", ["MySQL", "PostgreSQL"])
        host = st.text_input("Host", value="127.0.0.1")
        port = st.number_input("Port", value=3306 if db_type == "MySQL" else 5432)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        dbname = st.text_input("Database Name")

        if st.button("Connect"):
            if not dbname:
                st.error("Please provide a database name.")
            else:
                engine = create_db_engine(db_type, host, port, username, password, dbname)
                # Clear all session state on a new connection
                for key in st.session_state.keys():
                    del st.session_state[key]
                if engine:
                    st.session_state['db_engine'] = engine
                    st.session_state['db_name'] = dbname
                    # Automatically get and store the database version
                    st.session_state['db_version'] = get_db_version(engine)
                    st.success("Successfully connected!")
                    st.info(f"Database Version: {st.session_state['db_version']}")


    # --- Main App Logic ---
    if not configure_gemini(api_key):
        st.stop()

    if 'db_engine' not in st.session_state:
        st.info("Please connect to your database using the sidebar to begin.")
        return

    db_engine = st.session_state['db_engine']
    db_name = st.session_state['db_name']
    db_version = st.session_state['db_version'] # Get version from state
    
    # This block processes a question if one was submitted in the previous run
    if 'new_question' in st.session_state:
        question = st.session_state.pop('new_question') 
        
        with st.spinner("Thinking and fetching data..."):
            db_schema = get_db_schema(db_engine, db_name)
            db_dialect = db_engine.dialect.name
            # Pass auto-detected version to the LLM function
            sql_query, error = generate_sql_query(db_schema, db_dialect, db_version, question)

            st.session_state['query_details'] = {
                "question": question,
                "sql_query": sql_query,
                "error": error
            }

            if sql_query and sql_query.strip().upper().startswith("SELECT"):
                try:
                    result_df = pd.read_sql_query(sql_query, db_engine)
                    st.session_state['result_df'] = result_df
                except Exception as e:
                    st.session_state['query_details']['error'] = f"Error executing SQL query: {e}"

    # --- UI Layout ---
    st.subheader("Ask a question")
    
    text_col, button_col = st.columns([4, 1])
    with text_col:
        text_question = st.text_input("Type your question here:", label_visibility="collapsed", placeholder="e.g., What were the total sales last quarter?")
    with button_col:
        if st.button("Ask", key="ask_button", use_container_width=True):
            st.session_state['new_question'] = text_question
            if 'result_df' in st.session_state: del st.session_state['result_df']
            if 'query_details' in st.session_state: del st.session_state['query_details']
            st.rerun()

    audio_segment = audiorecorder("Or click to record your question", "Recording...")
    if audio_segment:
        question, error = transcribe_audio(audio_segment)
        if error:
            st.warning(error)
        else:
            st.session_state['new_question'] = question
            if 'result_df' in st.session_state: del st.session_state['result_df']
            if 'query_details' in st.session_state: del st.session_state['query_details']
            st.rerun()

    st.markdown("---")

    # --- Display Logic ---
    if 'query_details' in st.session_state:
        details = st.session_state['query_details']
        with st.expander("Query Details", expanded=True):
            st.write(f"**Your Question:** {details['question']}")
            if details['error']:
                st.error(details['error'])
            else:
                st.code(details['sql_query'], language="sql")

    if 'result_df' in st.session_state:
        st.subheader("Visualization")
        result_df = st.session_state['result_df']
        chart = create_smart_chart(result_df.copy())
        
        if chart == "metric": pass
        elif chart: st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No suitable chart could be generated. Displaying data table.")
            st.dataframe(result_df)

if __name__ == "__main__":
    main()
