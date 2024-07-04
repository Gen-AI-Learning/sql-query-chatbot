
import os
import re
import streamlit as st
import sqlite3
import uuid

from utilities.convertToList import convert_to_list
from typing import List


from dotenv import load_dotenv
from tabulate import tabulate



from langchain_openai import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType, AgentExecutor,create_tool_calling_agent
from langchain.tools import Tool
from langchain_community.utilities import SQLDatabase

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


from langchain.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate




load_dotenv()

#initialize llm model
chat = AzureChatOpenAI(
  openai_api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
  azure_deployment=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
  temperature=0,
  verbose=True
)

#Connect SQLite DB
print(os.getenv('DB_CONN_STRING'))
db = SQLDatabase.from_uri(os.getenv('DB_CONN_STRING'))




def get_table_names() -> List[str]:
  try:
    # This SQL query works for SQLite, MySQL, and PostgreSQL
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    result = convert_to_list(db.run(query))
    if isinstance(result, str):
      # If the result is a string, it's likely an error message
      print(f"Error querying table names: {result}")
      return []
    return [row[0] for row in result]
  except Exception as e:
    print(f"Error retrieving table names: {str(e)}")
    return []
  
import sqlite3

def get_table_schema(table_name: str) -> str:
  conn = None
  try:
    # Retrieve the database connection string from the environment variable
    db_conn_string = os.getenv('DB_CONN_STRING')
    db_file_path=None

    # Extract the file path from the connection string
    if db_conn_string.startswith('sqlite:///'):
      db_file_path = db_conn_string[10:]
    else:
      db_file_path = db_conn_string

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
        
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
        
    if not columns:
      return f"No schema information found for table '{table_name}'. The table might not exist."
        
    schema_info = f"Schema for table '{table_name}':\n"
    for col in columns:
      schema_info += f"- {col[1]} ({col[2]})\n"
        
    return schema_info
  except sqlite3.Error as e:
    return f"An error occurred while retrieving schema for table '{table_name}': {str(e)}"
  finally:
    if conn:
      conn.close()

    


# Initialize schema cache
schema_cache = {}


def get_cached_table_schema(table_name: str) -> str:
  if table_name not in schema_cache:
    schema_cache[table_name] = get_table_schema(table_name)
  return schema_cache[table_name]
  


def list_tables(*args, **kwargs) -> str:
    tables = get_table_names()
    print(f"Available tables: {', '.join(tables)}")
    return f"Available tables: {', '.join(tables)}"

class MoreDataException(Exception):
   def __init__(self, *args: object) -> None:
      super().__init__(*args)

def safe_sql_execute(query: str) -> str:
  # Check if the query contains INSERT, DELETE, or any other unwanted operations
    if re.search(r'\b(INSERT|DELETE|UPDATE|DROP|TRUNCATE|ALTER)\b', query, re.IGNORECASE):
        return "I'm sorry, but I can't perform INSERT, DELETE, or other data-modifying operations. I'm only able to retrieve information using SELECT queries. Could you please rephrase your request as a question about existing data?"
    
    try:
      result = db.run(query)  
     # Check if the result is a list
      if isinstance(result_list:=convert_to_list(result), list):
        if len(result_list) > 10:
          raise MoreDataException()
        else:
          # If records are 10 or below
          return str(result)
      else:
        return f"Query executed successfully. Result: {result}"

    except  MoreDataException as e:
       return (f"I found quite a lot of data in response to your query - more than 10 records. "
                        "To make the information more manageable, could you please ask for a summary instead? "
                        "For example, you could ask about the total count, average, maximum, or minimum values. "
                        "Or if you're looking for specific items, you could add more conditions to narrow down the results. "
                        "How would you like to refine your question?")
    except Exception as e:
        return f"I encountered an error while trying to answer your question: {str(e)}. Could you please rephrase your query or ask about a different aspect of the data?"



    

# Create a custom tool for safe SQL queries
safe_sql_tool = Tool(
  name="SafeSQLQueryTool",
  func=safe_sql_execute,
  description="Executes safe SQL queries (SELECT only) on the database. Does not allow INSERT, DELETE, or other data-modifying operations. Limits results strictly to 10 records."
)

# schema tool
cached_table_schema_tool = Tool(
    name="GetCachedTableSchemaTool",
    func=get_cached_table_schema,
    description="Retrieves the cached schema for a specific table. Input should be the table name."
)

# Tool to list table name
list_tables_tool = Tool(
    name="ListTablesTool",
    func=list_tables,
    description="Lists all available tables in the database."
)

# Initialize ConversationBufferMemory
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory = ChatMessageHistory(session_id="test-session")


# Create a custom prompt template
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are an AI assistant that helps with SQL queries. "
        "Before formulating queries, use the ListTablesTool to see available tables. "
        "Then, use the GetCachedTableSchemaTool to get schema information for specific tables you need. "
        "Use the SafeSQLQueryTool to execute queries. "
        "Consider the previous conversation when answering. "
        "If you don't know the answer, say that you don't know. "
        "If the result contains more than 10 records, strictly prohibit providing the records."
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

tools = [safe_sql_tool,cached_table_schema_tool, list_tables_tool]
agent = create_tool_calling_agent(
   llm=chat,
   tools=tools,
   prompt=prompt_template,
   
)

agent_executor = AgentExecutor(
   agent=agent,
   tools=tools,
   verbose=True
   )

agent_with_chat_history = RunnableWithMessageHistory(
   agent_executor,
   lambda session:memory,
   input_messages_key="input",
   history_messages_key="chat_history"

)

def generate_session_id():
   return str(uuid.uuid4())

def process_user_input(user_input,session_id):
  try:
    if user_input.lower() in ["clear", "exit"]:
      return "CLEAR_SESSION"
    config = {"configurable": {"session_id":session_id }}
    result=agent_with_chat_history.invoke({"input":user_input}, config=config)
      # result = agent.run(input=user_input)
    return result["output"]
  except Exception as e:
    return f"An error occurred: {str(e)}. Could you please rephrase your query or ask about a different aspect of the data?"


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
    st.experimental_rerun()
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
  st.experimental_rerun()



