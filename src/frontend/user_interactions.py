import streamlit as st
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder="Your DATA assistant here! Ask me anything about the Cruch Data Set  ...", 
                            label_visibility='hidden')
    return input_text
