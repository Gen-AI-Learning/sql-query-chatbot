import sqlite3
import re

from database.connection import db
from utils.convert_to_list import convert_to_list
from config.settings import DB_CONN_STRING
from exceptions.more_data_exception import MoreDataException
from typing import List



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
  


def get_table_schema(table_name: str) -> str:
  conn = None
  try:
    db_file_path=None

    # Extract the file path from the connection string
    if DB_CONN_STRING.startswith('sqlite:///'):
      db_file_path = DB_CONN_STRING[10:]
    else:
      db_file_path = DB_CONN_STRING
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


def safe_sql_execute(query: str) -> str:
  # Check if the query contains INSERT, DELETE, or any other unwanted operations
    if re.search(r'\b(INSERT|DELETE|UPDATE|DROP|TRUNCATE|ALTER)\b', query, re.IGNORECASE):
        return f"I'm sorry, but I can't perform INSERT, DELETE, or other data-modifying operations. I'm only able to retrieve information using SELECT queries. But I can provide the query for your question: {query}"
    
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
