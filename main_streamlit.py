import streamlit as st
from typing import Dict, List, Tuple
import pandas as pd
from src.clients.snowpark_client import SnowparkClient
from src.configs import CONFIG
from src.handlers import gpt_conversation
import logging
import logging.config
from src.frontend.user_interactions import get_text, initialize_session_variables


logging.config.dictConfig(CONFIG.LOG_CONFIG)

logger = logging.getLogger("SnowAI")

initialize_session_variables()

st.cache_resource()
def load_connection():
    """
    Load the connection to the Snowflake database.
    """
    logging.info("Loading Snowflake connection")
    snowflake_client = SnowparkClient(config=CONFIG.DATABASE)
    return snowflake_client

st.cache_data(ttl=3600)
def load_metadata(snowflake_client, databases_schemas):
    """
    Load the metadata from the Snowflake database.
    """
    logging.info("Loading Snowflake metadata")
    tables_metadata = snowflake_client.get_table_metadata(databases_schemas)
    return tables_metadata

def load_gpt_completion(query_text, tables_metadata):
    """
    Load the GPT-3 completion.
    """
    response_list = gpt_conversation.gpt_generate_response(query_text, tables_metadata)
    return response_list

st.cache_data(ttl=3600)
def load_data(snowflake_client, response_list):
    logging.error(f"Executing the following query: {response_list[0]}")
    df_snow = snowflake_client.session.sql(response_list[0])
    df_pandas = df_snow.to_pandas()  # this requires pandas installed in the Python environment
    return df_pandas.head(50)

def main():

    databases_schemas = ["CRUNCHBASE_BASIC_COMPANY_DATA.PUBLIC"]

    # Get Snowflake Session
    snowflake_client = load_connection()

    # Get database.schema metadata from Snowflake
    tables_metadata = load_metadata(snowflake_client, databases_schemas)

    # To move for a config file
    st.title("❄️ SnowAI - Data Requests")
    st.subheader("Powered by Snowpark, Streamlit and chatGPT")
    st.markdown(
        """
        <style>
        .title {
            font-size: 100px;
            color: white !important;
        }
        .top-left {
            position: absolute;
            top: 300
            left: 100;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Frontend - User input
    input_text = get_text()
    #input_text = st.text_area("What you want to know about the organizations? e.g 'How many companies have in San Franscisco?'")
    logging.info(f"User input: {input_text}")

    # Submit button for Snowflake query
    if st.button("Submit request"):
        response_list = load_gpt_completion(input_text, tables_metadata)

        # Check if is a valid query

        df_pandas = load_data(snowflake_client, response_list)
    
            # Use columns to display the three dataframes side-by-side along with their headers
        col1, _ = st.columns([3, 1])
        with st.container():
            with col1:
                st.subheader(response_list[1])
                st.dataframe(df_pandas)

if __name__ == "__main__":
    main()
