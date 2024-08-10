from langchain_community.utilities import SQLDatabase
from config.settings import DB_CONN_STRING
import time

# db = SQLDatabase.from_uri(DB_CONN_STRING)

class RefreshableDatabase:
    def __init__(self, conn_string, refresh_interval=300):  # 5 minutes default
        self.conn_string = conn_string
        self.refresh_interval = refresh_interval
        self.last_refresh_time = 0
        self.db = None
        self.refresh()

    def refresh(self):
        self.db = SQLDatabase.from_uri(self.conn_string)
        self.last_refresh_time = time.time()

    def get_db(self):
        if time.time() - self.last_refresh_time > self.refresh_interval:
            self.refresh()
        return self.db

    def force_refresh(self):
        self.refresh()


refreshable_db = RefreshableDatabase(DB_CONN_STRING)