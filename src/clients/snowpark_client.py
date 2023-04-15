import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark.session import Session
from typing import Dict, List
import pandas as pd

class SnowparkClient:
    """
    Object that connects to Snowflake service using Snowpark.
    """

    def __init__(self, config: dict):
        """
        Initializes the Snowpark client object.
        Parameters
        ----------
        config: dict
            Configuration object for the Snowflake database client.
        """
        self.logger = logging.getLogger("snowai.snowpark-client")

        snowflake_private_key = None
        if config["private_key"]:
            snowflake_private_key = self.decode_private_key(
                config["private_key"], config["private_key_passphrase"]
            )

        self.logger.info("Initializing SnowparkClient.")

        self.session = Session.builder.configs({
            "account":config["account"],
            "user":config["user"],
            "password":config["password"],
            "private_key":snowflake_private_key,
            "role":config["role"],
            "warehouse":config["warehouse"],
            "database":config["database"],
            "schema":config["schema"],
        }).create()
        
    def decode_private_key(self, private_key: str, pk_pass: str = None):
        """
        Decodes a RSA `.p8` private key.
        Parameters
        ----------
        private_key : str
            The path to the private key to be decoded
        pk_pass : str
            The passphrase used to decode the private_key
        Returns
        -------
        bytes
            the decoded private key
        """

        # convert empty strings in None or encode string if not empty
        pk_pass = pk_pass.encode() if pk_pass else None

        with open(private_key, "rb") as key:
            p_key = serialization.load_pem_private_key(
                key.read(), password=pk_pass, backend=default_backend()
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return pkb

    def execute_statement(self, stmt):
        """
        Executes a SQL statement.
        Parameters
        ----------
        stmt: str
            SQL statement to be executed.
        Returns
        ----------
        Execution results (as a DataFrame).
        """
        # Execute statement
        try:
            self.logger.debug(f"Executing statement: {stmt}")
            return self.session.sql(stmt).collect()

        # Handle errors
        except Exception as e:
            self.logger.error(f"Failed to execute statement: {e}.")
            raise Exception("Could not execute statement successfully.")

    def close(self):
        """
        Shutdown Snowpark client session.
        """
        self.logger.info("Snowpark client shutdown started.")
        self.session.close()
        self.logger.info("Snowpark client shutdown complete.")

    def get_table_metadata(self, db_schema_list: List[str]):
        """
        Retrieves table and view metadata from the provided databases and schemas.

        """
        self.logger.info("Table and view metadata retrieval started.")
        metadata_list = []

        for db_schema in db_schema_list:
            try:
                db, schema = db_schema.split('.')
                self.logger.info(f"Retrieving table and view metadata from {db}.{schema}")

                # Retrieve tables and views from the information schema
                stmt = f"SELECT TABLE_NAME, TABLE_TYPE FROM {db}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{schema}';"
                objects = self.execute_statement(stmt)

                # Convert the list to a DataFrame
                objects_df = pd.DataFrame(objects, columns=['table_name', 'table_type'])
                #self.logger.debug(f"Objects in {db}.{schema}:\n{objects_df.to_string()}")

                for _, obj in objects_df.iterrows():
                    object_name = obj['table_name']
                    object_type = obj['table_type']

                    # Retrieve columns and data types for tables and views
                    column_stmt = f"SELECT COLUMN_NAME, DATA_TYPE FROM {db}.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{object_name}';"
                    columns = self.execute_statement(column_stmt)

                    columns_df = pd.DataFrame(columns, columns=['column_name', 'data_type'])
                    columns_str = columns_df.to_string(index=False)
                    metadata_list.append(f"{db}.{schema}.{object_name} ({object_type})\n{columns_str}\n")

            except Exception as e:
                self.logger.error(f"Failed to retrieve table and view metadata from {db_schema}: {e}")
                self.logger.exception("Exception occurred")
                raise Exception(f"Could not retrieve table and view metadata from {db_schema} successfully.")

        metadata_str = '\n'.join(metadata_list)
        self.logger.info("Table and view metadata retrieval complete.")
        return metadata_str
