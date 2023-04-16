import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark.session import Session
from typing import Dict, List
import pandas as pd
import streamlit as st

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
            "client_session_keep_alive":config["client_session_keep_alive"],
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

    def close(self):
        """
        Shutdown Snowpark client session.
        """
        self.logger.info("Snowpark client shutdown started.")
        self.session.close()
        self.logger.info("Snowpark client shutdown complete.")

