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

# Getting Metadata from Snowflake
tables_metadata = snowpark_client.get_table_metadata(source)

############################################
#  Testing gpt_generate_response function           
response_list = gpt_generate_response(query_text, tables_metadata)


# Create function the  
df_snow = snowpark_client.session.sql(response_list[0])
df = df_snow.to_pandas()  # this requires pandas installed in the Python environment


#Create a table using the DataFrame columns and data
fig = go.Figure(data=[go.Table(header=dict(values=list(df.columns)),
                               cells=dict(values=[df[col] for col in df.columns]))
                     ])

# Customize the table appearance
fig.update_layout(title=response_list[1])

# Show the table
fig.show()
