import streamlit as st
import pandas as pd
from audiorecorder import audiorecorder

# Import utility functions from our other files
from database import create_db_engine, get_db_schema
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

    # --- Sidebar for Database Connection ---
    with st.sidebar:
        st.header("Database Connection")
        
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
                # Clear previous state on new connection attempt
                for key in ['db_engine', 'db_name', 'query_info', 'result_df']:
                    if key in st.session_state:
                        del st.session_state[key]

                if engine:
                    st.session_state['db_engine'] = engine
                    st.session_state['db_name'] = dbname
                    st.success("Successfully connected!")
                # No 'else' needed, state is already cleared

    # --- Main App Logic ---
    if 'db_engine' not in st.session_state:
        st.info("Please connect to your database using the sidebar to begin.")
        return

    db_engine = st.session_state['db_engine']
    db_name = st.session_state['db_name']
    
    st.header("Ask me anything about your data...")
    audio_segment = audiorecorder("Click to record", "Recording...")
    
    if audio_segment:
        st.session_state['audio_segment'] = audio_segment
        # Clear previous results when a new question is asked
        for key in ['query_info', 'result_df']:
            if key in st.session_state:
                del st.session_state[key]

    with st.expander("View Database Schema", expanded=False):
        schema = get_db_schema(db_engine, db_name)
        st.markdown(f"```sql\n{schema}\n```")

    # Process audio and display results
    if 'audio_segment' in st.session_state and 'query_info' not in st.session_state:
        audio_segment = st.session_state.pop('audio_segment')
        
        question, error = transcribe_audio(audio_segment)
        if error:
            st.warning(error)
            return

        with st.spinner("Thinking..."):
            db_schema = get_db_schema(db_engine, db_name)
            db_dialect = db_engine.dialect.name
            sql_query, error = generate_sql_query(db_schema, db_dialect, question)
        
        # Store all query info in a single session state object
        st.session_state['query_info'] = {
            "question": question,
            "sql_query": sql_query,
            "error": error
        }

    # Display results if they exist in the session state
    if 'query_info' in st.session_state:
        info = st.session_state['query_info']
        st.write(f"**You said:** {info['question']}")

        if info['error']:
            st.error(info['error'])
            return

        cleaned_query = info['sql_query'].strip()
        
        if cleaned_query.upper().startswith("SELECT"):
            st.code(cleaned_query, language="sql")
            with st.spinner("Executing query..."):
                try:
                    result_df = pd.read_sql_query(cleaned_query, db_engine)
                    st.session_state['result_df'] = result_df # Store df for charting
                except Exception as e:
                    st.error(f"Error executing SQL query: {e}")
                    if 'result_df' in st.session_state:
                        del st.session_state['result_df']
        else:
            st.info("The AI provided the following explanation:")
            st.markdown(f"```sql\n{cleaned_query}\n```")
    
    # Display chart/data if a dataframe exists
    if 'result_df' in st.session_state:
        st.subheader("Visualization")
        result_df = st.session_state['result_df']
        chart = create_smart_chart(result_df.copy()) # Use copy to avoid caching issues
        
        if chart == "metric":
            pass
        elif chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No suitable chart could be generated. Displaying data table.")
            st.dataframe(result_df)

if __name__ == "__main__":
    if configure_gemini():
        main()
