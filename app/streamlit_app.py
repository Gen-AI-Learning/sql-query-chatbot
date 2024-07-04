import streamlit as st
from ai.agent import process_user_input
from utils.session_management import generate_session_id

def run_app():
  st.title("SQL Query Chatbot")
  st.write("Welcome to the Safe SQL Query Assistant!")
  st.write("You can ask questions about the database, and I'll try to answer them.")
  st.write("Note: This assistant can only perform SELECT queries and is limited to returning 10 records.")
  st.write("Type 'clear' or 'exit' to start a new chat.")

  if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
  # Initialize chat history
  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

  # React to user input
  if prompt:= st.chat_input("What would you like to know about the database?"):
    # Display user message in chat message container
    with st.chat_message("user"):
      st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role":"user","content":prompt})

    response = process_user_input(prompt, st.session_state.session_id)

    if response == "CLEAR_SESSION":
      # Clear the chat history and generate a new session ID
      st.session_state.messages = []
      st.session_state.session_id = generate_session_id()
      st.rerun()
    else:
      # Display assistant response in chat message container
      with st.chat_message("assistant"):
        st.markdown(response)
      # Add assistant response to chat history
      st.session_state.messages.append({"role": "assistant", "content": response})

  # Add a button to clear the session
  if st.button("Clear Session"):
    st.session_state.messages = []
    st.session_state.session_id = generate_session_id()
    st.rerun()
