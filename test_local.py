from src.handlers.gpt_conversation import gpt_generate_response
from src.configs import CONFIG
import logging
import logging.config
import re
import ast
import pandas as pd
import plotly.graph_objects as go

logging.config.dictConfig(CONFIG.LOG_CONFIG)

# Testing gpt_generate_text function 
#tables_metadata = "table name: organization_summary, columns(name:varchar,  region:varchar, created_at:timestamp, country:varchar, type:varchar)"
query_text = "Cities with more organizations"

#############################################
# Testing Snowpark Client
from src.clients.snowpark_client import SnowparkClient
snowpark_client = SnowparkClient(config=CONFIG.DATABASE)

source = ["CRUNCHBASE_BASIC_COMPANY_DATA.organization_summary"]

import logging
import logging.config

from typing import Dict, List, Tuple

import pandas as pd
import snowflake.connector.errors

import streamlit as st

from src.clients.snowpark_client import SnowparkClient
from src.configs import CONFIG
from src.frontend.user_interactions import get_text, initialize_session_variables

logging.config.dictConfig(CONFIG.LOG_CONFIG)


DATABASE_SCHEMAS = ["CRUNCHBASE_BASIC_COMPANY_DATA.PUBLIC"]

@st.cache_resource
def innit_connection():
    """
    Load the connection to the Snowflake database.
    """
    logging.info("Loading Snowflake connection")
    snowflake_client = SnowparkClient(config=CONFIG.DATABASE)
    return snowflake_client

conn = innit_connection()


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

            metadata_list.append(f"{db}.{schema}.{object_name}: {column_info}")

    metadata_str = '\n'.join(metadata_list).replace(' - None', '')
    logging.info("Table and view metadata retrieval complete.")
    return metadata_str

text =  get_table_metadata(DATABASE_SCHEMAS)

print (text)
