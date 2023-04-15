import streamlit as st

def initialize_session_variables():
    """
    Initialize the session variables.
    """
    if "input" not in st.session_state:
        st.session_state["input"] = ""

def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    placeholder = "I'm your DATA assistant! Ask me anything about the Crucchbase Basic Company Data ..."
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder=placeholder, 
                            label_visibility='hidden')
    return input_text
