from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (BaseChatMessageHistory, InMemoryChatMessageHistory)



from ai.tools import safe_sql_tool, cached_table_schema_tool, list_tables_tool, spelling_correction_tool
from config.settings import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
from database.connection import refreshable_db



#initialize llm model
chat = AzureChatOpenAI(
  openai_api_version=AZURE_OPENAI_API_VERSION,
  azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
  temperature=0,
  verbose=True
)

# memory = ChatMessageHistory(session_id="test-session")

# Create a custom prompt template
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
      "You are an AI assistant specializing in helping users with SQL queries. Your responses should be concise, friendly, and easy to understand."
    "\n\nFor each user request, follow these steps:"
    "\n1.Must Use the 'spellingCorrection' tool to fix any spelling mistakes in the user's input related to table names, column names, or predefined values."
    "\n2. Use the 'ListTablesTool' to provide the user with a list of available tables in the database."
    "\n3. Use the 'GetCachedTableSchemaTool' to retrieve and share the schema information for relevant tables."
    "\n4. Analyze the user's request and the schema to formulate an appropriate SQL query."
    "\n5. For SELECT queries, use the 'SafeSQLQueryTool' to execute the query and return the results, limiting the output to a maximum of 10 records."
    "\n6. For non-SELECT queries (INSERT, UPDATE, DELETE, etc.), provide the SQL query but do not execute it."
    "\n7. If you're unsure or don't have enough information to provide a complete answer, ask the user for clarification instead of giving a lengthy explanation."
    "\n8. Explain your reasoning and any assumptions made when formulating queries, but keep your responses concise."
    "\n11. If a query would return more than 10 records, mention this in your response and suggest ways to limit the result set."
    "\n\nRemember, your primary goal is to assist the user with SQL queries in a friendly and helpful manner."
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

tools = [safe_sql_tool,cached_table_schema_tool, list_tables_tool, spelling_correction_tool]
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

# Function to get or create ChatMessageHistory for a session
# def get_chat_history(session_id: str) -> ChatMessageHistory:
#   return ChatMessageHistory(session_id=session_id)

store = {}
def get_chat_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  print("Memory:", store[session_id])
  return store[session_id]
  

agent_with_chat_history = RunnableWithMessageHistory(
   agent_executor,
   get_chat_history,
   input_messages_key="input",
   history_messages_key="chat_history",

)

def process_user_input(user_input:str, session_id:str):

  print(f"My session Id: {session_id}")
  try:
    refreshable_db.force_refresh()
    if user_input.lower() in ["clear", "exit"]:
      return "CLEAR_SESSION"
    config = {"configurable": {"session_id":session_id }}
    result=agent_with_chat_history.invoke({"input":user_input}, config=config)
      # result = agent.run(input=user_input)
    return result["output"]
  except Exception as e:
    return f"An error occurred: {str(e)}. Could you please rephrase your query or ask about a different aspect of the data?"
