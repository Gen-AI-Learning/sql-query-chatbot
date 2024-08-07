from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder



from ai.tools import safe_sql_tool, cached_table_schema_tool, list_tables_tool, spelling_correction_tool
from config.settings import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME



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
       "You are an AI assistant specializing in SQL queries. Follow these steps for each request:"
        "\n1. Use spellingCorrection to correct any potential spelling mistakes in the user's query regarding table names, column names, and predefined values."
    "\n2. Use ListTablesTool to identify available tables."
    "\n3. Use GetCachedTableSchemaTool to retrieve schema information for relevant tables."
    "\n4. Analyze the user's request and the schema to formulate an appropriate SQL query."
    "\n5. For SELECT queries, use SafeSQLQueryTool to execute and retrieve results."
    "\n6. For non-SELECT queries (INSERT, UPDATE, DELETE, etc.), formulate the query but do not execute it."
    "\n7. Always include the SQL query in your response, whether executed or not."
    "\n8. Limit result outputs to a maximum of 10 records."
    "\n9. Consider the conversation history when formulating responses."
    "\n10. If you're unsure or don't have enough information, ask for clarification."
    "\n11. Explain your reasoning and any assumptions made when formulating queries."
    "\n12. If a query would return more than 10 records, mention this in your response and suggest ways to limit the result set."
    "\n13. Provide clear explanations of the query structure and purpose."
    "\nRemember: Your primary goal is to assist with SQL queries while adhering to these guidelines."
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
def get_chat_history(session_id: str) -> ChatMessageHistory:
  return ChatMessageHistory(session_id=session_id)

agent_with_chat_history = RunnableWithMessageHistory(
   agent_executor,
   get_chat_history,
   input_messages_key="input",
   history_messages_key="chat_history"

)

def process_user_input(user_input:str, session_id:str):
  try:
    if user_input.lower() in ["clear", "exit"]:
      return "CLEAR_SESSION"
    config = {"configurable": {"session_id":session_id }}
    result=agent_with_chat_history.invoke({"input":user_input}, config=config)
      # result = agent.run(input=user_input)
    return result["output"]
  except Exception as e:
    return f"An error occurred: {str(e)}. Could you please rephrase your query or ask about a different aspect of the data?"
