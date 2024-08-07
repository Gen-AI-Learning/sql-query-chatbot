from langchain.tools import Tool, StructuredTool
from database.queries import safe_sql_execute, get_cached_table_schema, list_tables
from utils.spelling_corrector import spelling_corrector

def correct_spelling_tool(query: str) -> str:
    return spelling_corrector.correct_spelling(query)



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
# Spelling correction tool
spelling_correction_tool = Tool(
    name="spellingCorrection",
    func=correct_spelling_tool,
    description="Useful for correcting spellings of table names, column names, and predefined values in a query."
)
