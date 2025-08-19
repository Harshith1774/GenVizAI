import streamlit as st
import pandas as pd
from audiorecorder import audiorecorder

# Import utility functions from our other files
from database import create_db_engine, get_db_schema
from llm import configure_gemini, generate_sql_query
from speech import transcribe_audio

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
                if engine:
                    # Store connection info in session state
                    st.session_state['db_engine'] = engine
                    st.session_state['db_name'] = dbname
                    st.success("Successfully connected!")
                else:
                    # Clear session state on failed connection
                    if 'db_engine' in st.session_state:
                        del st.session_state['db_engine']
                    if 'db_name' in st.session_state:
                        del st.session_state['db_name']

    # --- Main App Logic ---
    # Only show the main interface if the database is connected
    if 'db_engine' not in st.session_state:
        st.info("Please connect to your database using the sidebar to begin.")
        return

    db_engine = st.session_state['db_engine']
    db_name = st.session_state['db_name']
    
    col1, col2 = st.columns(2)

    with col1:
        st.header("Ask me anything about your data...")
        audio_segment = audiorecorder("Click to record", "Recording...")
        
        # If a new recording is made, store it in session state to be processed
        if audio_segment:
            st.session_state['audio_segment'] = audio_segment

    with col2:
        with st.expander("View Database Schema", expanded=False):
            schema = get_db_schema(db_engine, db_name)
            st.text(schema)

    # Process the audio recording only once after it's made
    if 'audio_segment' in st.session_state:
        audio_segment = st.session_state.pop('audio_segment')
        
        # 1. Transcribe Audio
        question, error = transcribe_audio(audio_segment)
        if error:
            st.warning(error)
            return
        st.write(f"**You said:** {question}")

        # 2. Generate SQL
        with st.spinner("Thinking..."):
            db_schema = get_db_schema(db_engine, db_name)
            db_dialect = db_engine.dialect.name
            
            sql_query, error = generate_sql_query(db_schema, db_dialect, question)
            if error:
                st.error(error)
                return

        # --- Corrected Logic Block ---
        # 3. Execute SQL or Display AI's message
        # Clean the string again to be extra safe before checking
        cleaned_query = sql_query.strip()
        
        if cleaned_query.upper().startswith("SELECT"):
            st.code(cleaned_query, language="sql")
            with st.spinner("Executing query..."):
                try:
                    result_df = pd.read_sql_query(cleaned_query, db_engine)
                    st.dataframe(result_df)
                except Exception as e:
                    st.error(f"Error executing SQL query: {e}")
        else:
            # If it's not a SELECT query, it's a message from the AI
            st.info("The AI provided the following explanation:")
            st.markdown(f"```sql\n{cleaned_query}\n```")
        # --- End of Corrected Logic ---


if __name__ == "__main__":
    # Configure the Gemini API at the start of the app
    if configure_gemini():
        main()
