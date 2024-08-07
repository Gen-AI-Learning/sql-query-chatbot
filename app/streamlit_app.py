import streamlit as st
from ai.agent import process_user_input
from utils.session_management import generate_session_id

def run_app():
  # App title and description
  st.title("Smart Query Chatbot")
  st.write("""
  <style>
      .main {background-color: #f1f3f4;}
      .css-18e3th9 {padding-top: 3rem; padding-bottom: 3rem;}
      .st-bb {background-color: #ffffff; border: 1px solid #e0e0e0; padding: 10px; border-radius: 8px;}
      .st-dx {border: 1px solid #e0e0e0; border-radius: 8px;}
      .stButton>button {background-color: #1a73e8; color: #ffffff; border-radius: 5px; padding: 10px 20px;}
      .stTextInput>div>div>input {border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px;}
      .stTextInput>div>div {border: 1px solid #e0e0e0; border-radius: 8px;}
  </style>
  """, unsafe_allow_html=True)
  st.write("Welcome to the Safe SQL Query Assistant! You can ask questions about the database, and I'll try to answer them. Note: This assistant can only perform SELECT queries and is limited to returning 10 records. Type 'clear' or 'exit' to start a new chat.")

  # Initialize session state
  if "session_id" not in st.session_state:
      st.session_state.session_id = generate_session_id()

  if "messages" not in st.session_state:
      st.session_state.messages = []

  # Display chat history
  for message in st.session_state.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])

  # React to user input
  if prompt := st.chat_input("What would you like to know about the database?"):
      with st.chat_message("user"):
          st.markdown(prompt)
      st.session_state.messages.append({"role": "user", "content": prompt})

      # Show a spinner while processing the input
      with st.spinner("Thinking..."):
          response = process_user_input(prompt, st.session_state.session_id)

      if response == "CLEAR_SESSION":
          st.session_state.messages = []
          st.session_state.session_id = generate_session_id()
          st.experimental_rerun()
      else:
          with st.chat_message("assistant"):
              st.markdown(response)
          st.session_state.messages.append({"role": "assistant", "content": response})

  # Add a button to clear the session
  if st.button("Clear Session"):
      st.session_state.messages = []
      st.session_state.session_id = generate_session_id()
      st.experimental_rerun()