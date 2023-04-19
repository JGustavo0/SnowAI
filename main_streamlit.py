import logging
import logging.config

from typing import Dict, List, Tuple

import pandas as pd
import snowflake.connector.errors

import os

import streamlit as st

from src.clients.snowpark_client import SnowparkClient
from src.configs import CONFIG
from src.frontend.user_interactions import get_text, initialize_session_variables
from src.handlers import gpt_conversation


logging.config.dictConfig(CONFIG.LOG_CONFIG)

logger = logging.getLogger("SnowAI")

initialize_session_variables()

DATABASE_SCHEMAS = os.getenv("DATABASE_SCHEMAS", "CRUNCHBASE_BASIC_COMPANY_DATA.PUBLIC,STREAMLIT_DB.PUBLIC").split(",")

st.set_page_config(
     page_title="SnowAI - Automated Data Requests",
     page_icon="☃️",
     layout="centered",
     initial_sidebar_state="auto",
     menu_items={
         'Get Help': 'https://app.snowflake.com/marketplace/listing/GZSNZ7BXU9/crunchbase-crunchbase-basic-company-data',
         'About': "This app uses [chatGPT](https://chatgpt.com) to generate responses to user requests. The app is built using [Streamlit](https://streamlit.io) and [Snowpark](https://docs.snowflake.com/en/user-guide/snowpark-overview.html).",
     }
)

st.header("❄️ SnowAI - Automated Data Requests")
st.caption("Powered by Snowpark, Streamlit and chatGPT - For this demo, we are using the [Crunch Company Data Set](https://app.snowflake.com/marketplace/listing/GZSNZ7BXU9/crunchbase-crunchbase-basic-company-data) from Snowflake Marketplace.")


st.markdown(
        """
        <style>
        .title {
            font-size: 100px;
            color: white !important;
        }
        .top-left {
            position: absolute;
            top: 300;
            left: 100;
        }
        .css-16idsys p {
            word-break: break-word;
            margin-bottom: 0px;
            font-size: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

@st.cache_resource
def innit_connection():
    """
    Load the connection to the Snowflake database.
    """
    logging.info("Loading Snowflake connection")
    snowflake_client = SnowparkClient(config=CONFIG.DATABASE)
    return snowflake_client

conn = innit_connection()

@st.cache_data(ttl=600)
def run_query(stmt):
    try:
        logging.debug(f"Executing statement: {stmt}")
        return conn.session.sql(stmt).to_pandas()

    except snowflake.connector.errors.ProgrammingError as e:
        logging.error(f"Failed to execute statement: {e}")
        raise snowflake.connector.errors.ProgrammingError("Could not execute statement successfully.")

def get_table_metadata(db_schema_list: List[str]):
    """
    Retrieves table and view metadata from the provided databases and schemas.

    """
    if not db_schema_list:
        raise ValueError("db_schema_list cannot be empty")

    metadata_list = []

    for db_schema in db_schema_list:
        try:
            db, schema = db_schema.split('.')
        except ValueError:
            raise ValueError(f"Invalid format for db_schema: {db_schema}. Expected format is <database_name>.<schema_name>")

        logging.info(f"Retrieving table and view metadata from {db}.{schema}")

        # Retrieve tables and views from the information schema
        stmt = f"SELECT TABLE_NAME, TABLE_TYPE FROM {db}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{schema}' ORDER BY TABLE_NAME, TABLE_TYPE ;"
        objects = run_query(stmt)

        logging.debug(f"Objects in {db}.{schema}:\n{objects.to_string()}")

        for _, obj in objects.iterrows():
            object_name = obj['TABLE_NAME']
            object_type = obj['TABLE_TYPE']

            # Retrieve columns and data types for tables and views
            column_stmt = f"SELECT COLUMN_NAME, DATA_TYPE, COMMENT FROM {db}.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{object_name}' ORDER BY COLUMN_NAME, DATA_TYPE;"
            columns = run_query(column_stmt)

            if columns.empty:
                logging.warning(f"{db}.{schema}.{object_name} has no columns, skipping.")
                continue

            column_names = columns['COLUMN_NAME'].to_list()
            data_types = columns['DATA_TYPE'].to_list()
            column_comments = columns['COMMENT'].to_list()

            column_info = ", ".join([f"{name} ({data_type}) - {comment}" for name, data_type, comment in zip(column_names, data_types, column_comments)])

            metadata_list.append(f" Database.Table: {db}.{schema}.{object_name}: {column_info}")

    metadata_str = '\n'.join(metadata_list).replace(' - None', '')
    logging.info("Table and view metadata retrieval complete.")
    return metadata_str

if __name__ == "__main__":
    
    ### Get database.schema metadata from Snowflake
    tables_metadata = get_table_metadata(DATABASE_SCHEMAS)

    input_text = get_text()
    logging.info(f"User input: {input_text}")

    # Get GPT-3 completion
    response_list = gpt_conversation.gpt_generate_response(input_text, tables_metadata)
    query = response_list[0]

    if st.button("Submit request"):
        df_snow = run_query(query)
        if query != 'SELECT 1':
            st.subheader(response_list[1])
            st.dataframe(df_snow)
        else:
            st.write("Ups 🤖! Sorry, no results! \n Note that I have access to the tables/views in following database(s):")
            st.code(tables_metadata)

        if st.button("Clear and try other request"):
            st.experimental_rerun()
