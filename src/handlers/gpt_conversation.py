import openai
from src.configs import CONFIG
import re
import ast
import logging
from openai.error import OpenAIError

def generate_messages(query_text: str, tables_metadata: dict) -> list:
    """
    Generates a list of messages for the GPT to process.
    
    :param query_text: The user query text.
    :param tables_metadata: The metadata of tables to be used for query generation.
    :return: A list of messages.
    """
    messages = [
        {"role": "system", "content": "Act as Data Engineer, specialist in Snowflake Snowpark"},
        {"role": "system", "content": "I will ask you for a query in snowpark format"},
        {"role": "system", "content": "Print only the Python list: [<a single line of code>, <Resumed title)>]"},
        {"role": "system", "content": "Print ONLY the code, no context, no anything else"},
        {"role": "system", "content": "Assume that Session obj was created - from snowflake.snowpark import session)"},
        {"role": "system", "content": f"Use the following tables metadata {tables_metadata} to build the query" },
        {"role": "user", "content": "Give me the companies headquartered in San Francisco"},
        {"role": "assistant", "content": '["SELECT * FROM organization_summary WHERE city=\'San Francisco\' limit 10", "San Francisco companies"]'},
        {"role": "user", "content": "A list of companies related to robotics"},
        {"role": "assistant", "content": '["SELECT * FROM organization_summary WHERE short_description like \'%robotics%\' limit 10", "Robotics companies"]'},
        {"role": "user", "content": f"{query_text}"}
    ]
    return messages

def gpt_generate_response(query_text: str, tables_metadata: dict) -> list:
    """
    Generates a response from GPT based on the given query text and tables metadata.
    
    :param query_text: The user query text.
    :param tables_metadata: The metadata of tables to be used for query generation.
    :return: A list containing the generated query and title.
    """
    ERROR_MESSAGE = "Ups 🤖! Time to call the 🕵️‍♂️ Data Analyst to save the day! 💪"

    try:
        # Set the API key
        openai.api_key = CONFIG.CHATGPT["api_key"]

        # Generate the messages
        messages = generate_messages(query_text, tables_metadata) 
        
        logging.info(f"Generated messages: {messages}")

        completion = openai.ChatCompletion.create(
            model=CONFIG.CHATGPT["model"],
            messages=messages
        )
        # Extract the data between square brackets
        data_str = re.search(r'\[([\s\S]*)\]', completion.choices[0].message.content).group(0)
        # Convert the extracted string to a Python list
        response_list = ast.literal_eval(data_str)
    except OpenAIError as e:
        # Handle exceptions and log errors
        logging.error(f"An error occurred while generating a response from GPT: {str(completion.choices[0].message.content)}")
        # Create a dummy list as fallback
        response_list = ["SELECT 1", ERROR_MESSAGE]
    except AttributeError as e:
        # Handle exceptions and log errors for re.search()
        logging.error(f"An error occurred while extracting data using re.search(): {str(e)}")
        # Create a dummy list as fallback
        response_list = ["SELECT 1", ERROR_MESSAGE]

    return response_list
