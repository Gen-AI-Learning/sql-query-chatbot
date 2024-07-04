# SQL Query Chatbot

## Description

SQL Query Chatbot is an intelligent assistant designed to help users interact with a SQL database using natural language. Built with Streamlit and powered by Azure OpenAI's language models, this application allows users to ask questions about the database and receive answers without writing SQL queries directly.

## Features

- Natural language interface for SQL queries
- Safe SQL execution (SELECT queries only)
- Dynamic table schema retrieval
- Session management for personalized interactions
- Limit of 10 records per query to manage data volume
- Clear session functionality

## Tech Stack

- Python 3.8+
- Streamlit
- Langchain
- Azure OpenAI
- SQLite (can be adapted for other SQL databases)

## Installation

1. Clone the repository:
   git clone https://github.com/Gen-AI-Learning/sql-query-chatbot.git
   cd sql-query-chatbot

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate # On Windows use venv\Scripts\activate

3. Install the required packages:
   pip install -r requirements.txt

4. Set up your environment variables:
   Create a `.env` file in the root directory and add the following:

DB_CONN_STRING=sqlite:///path/to/your/database.db
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your_deployment_name

## Usage

1. Start the Streamlit app:
   streamlit run main.py

2. Open your web browser and go to `http://localhost:8501`.

3. Start interacting with the chatbot by asking questions about your database.

## Example Queries

- "What tables are available in the database?"
- "Show me the schema of the users table."
- "Give me the names of the first 5 users."
- "What is the average age of users?"

## Project Structure

sql_query_chatbot/
│
├── main.py
├── requirements.txt
├── .env
│
├── app/
│ └── streamlit_app.py
│
├── config/
│ └── settings.py
│
├── database/
│ ├── connection.py
│ └── queries.py
│
├── ai/
│ ├── agent.py
│ └── tools.py
│
└── utils/
├── convert_to_list.py
└── session_management.py
