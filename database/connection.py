from langchain_community.utilities import SQLDatabase
from config.settings import DB_CONN_STRING

db = SQLDatabase.from_uri(DB_CONN_STRING)