from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os
import psycopg2
from Utils.logger import setup_logger

logger = setup_logger()

class DB_auth():
    def __init__(self):
        load_dotenv()
        self.dbname = os.getenv('DB_Name')
        self.dbusername = os.getenv('DB_UserName')
        self.dbpassword = os.getenv('DB_Password')
        self.dbport = os.getenv('DB_port')
        self.host = os.getenv('DB_Host', 'localhost')
        self.dbdrivername = "postgresql+psycopg2"

    def create_engine(self):
        try:
            conn_string = URL.create(
                drivername=self.dbdrivername,
                username=self.dbusername,
                password=self.dbpassword,
                host=self.host,
                port=self.dbport,
                database=self.dbname
            )
            logger.info(f"Connecting to {self.host}:{self.dbport}/{self.dbname} as {self.dbusername}")
            engine = create_engine(conn_string)
            
            # test connection
            with engine.connect() as conn:
                logger.info("Database connection established successfully!")
                return engine
        
        except Exception as e:
            logger.info(f"Failed to create SQLAlchemy engine: {e}")
            return None