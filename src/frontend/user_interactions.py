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
    
    placeholder = "How many companies are based in San Franscisco?"
    input_text = st.text_input("I'm your 🤖 DATA assistant! What do you want to know about the companies summary? 🏢💡", st.session_state["input"], key="input",
                            placeholder=placeholder, 
                            label_visibility='visible')
    return input_text
