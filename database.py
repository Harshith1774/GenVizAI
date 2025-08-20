import streamlit as st
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

@st.cache_resource
def create_db_engine(db_type, host, port, username, password, dbname):
    """
    Creates and caches a SQLAlchemy engine to avoid reconnecting on every script rerun.
    """
    try:
        if db_type == "MySQL":
            drivername = "mysql+pymysql"
        elif db_type == "PostgreSQL":
            drivername = "postgresql+psycopg2"
        else:
            st.error(f"Unsupported database type: {db_type}")
            return None

        # Create a structured URL to prevent connection string errors
        connection_url = URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=dbname if dbname else None
        )
        
        engine = create_engine(connection_url)
        # Test the connection to ensure it's valid
        with engine.connect():
            pass
        
        return engine
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def get_db_schema(engine, db_name):
    """
    Inspects the database and returns a string representation of the schema,
    including tables and views.
    """
    if not engine or not db_name:
        return "Database not connected or database name not provided."
        
    try:
        inspector = inspect(engine)
        schema_info = f"Schema for database **`{db_name}`**:\n\n"
        
        # Get table information
        tables = inspector.get_table_names(schema=db_name)
        if tables:
            schema_info += "**Tables:**\n"
            for table_name in tables:
                columns = inspector.get_columns(table_name, schema=db_name)
                schema_info += f"- `{table_name}`: " + ", ".join([f"{col['name']} ({col['type']})" for col in columns]) + "\n"

        # Get view information
        views = inspector.get_view_names(schema=db_name)
        if views:
            schema_info += "\n**Views (query as tables):**\n"
            for view_name in views:
                columns = inspector.get_columns(view_name, schema=db_name)
                schema_info += f"- `{view_name}`: " + ", ".join([f"{col['name']} ({col['type']})" for col in columns]) + "\n"
                
        return schema_info if tables or views else f"No tables or views found in the database '{db_name}'."
    except Exception as e:
        return f"Error fetching schema: {e}"
