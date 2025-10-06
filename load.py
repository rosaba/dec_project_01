from sqlalchemy.engine import Engine,URL
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
import psycopg2

def create_db_url(username, password, host, port, database) ->  URL:

    source_connection_url = URL.create(
        drivername = 'postgresql+psycopg2',
        username = username,
        password = password,
        host = host,
        port = port,
        database = database
    )

    return source_connection_url

def check_connection(source_connection_url:URL) -> bool:

    try:
        source_engine = create_engine(source_connection_url)
        with source_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except:
        return False

if __name__ == '__main__':

    load_dotenv()
    username = os.environ.get('DESTINATION_DB_USERNAME')
    password = os.environ.get('DESTINATION_DB_PASSWORD')
    host = os.environ.get('DESTINATION_SERVER_NAME')
    port = os.environ.get('DESTINATION_PORT')
    database = os.environ.get('DESTINATION_DATABASE_NAME')

    source_url = create_db_url(username, password, host, port, database)

    if check_connection(source_url):
        print('Connection Successful')
    else:
        print('Connection failed! Please check configuration!')

