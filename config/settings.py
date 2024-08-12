import os
from dotenv import load_dotenv

load_dotenv()

DB_CONN_STRING = os.getenv('DB_CONN_STRING')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
