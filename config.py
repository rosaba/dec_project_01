import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from loguru import logger

class APIConfig:

    def __init__(self,base_url=None):
        load_dotenv()
        self.base_url = base_url
        self.app_token = os.environ.get('X-APP-TOKEN')
    
    def get_headers(self):
        return {'X-App-Token': self.app_token}

class DatabaseConfig:

    def __init__(self):
        self.username = os.environ.get('DESTINATION_DB_USERNAME')
        self.password = os.environ.get('DESTINATION_DB_PASSWORD')
        self.host = os.environ.get('DESTINATION_SERVER_NAME')
        self.port = os.environ.get('DESTINATION_PORT')
        self.database = os.environ.get('DESTINATION_DATABASE_NAME')
    
    def create_url(self):

        source_url = URL.create(
            drivername='postgresql+psycopg2',
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

        return source_url