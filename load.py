from sqlalchemy.engine import Engine,URL
from sqlalchemy import create_engine,text, Table, Column, MetaData, Integer, String, Float, Date, Time, Text, DateTime
from dotenv import load_dotenv
import os
import psycopg2
import yaml

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

def get_type(type_str):

    type_mapping = {
        'Date' : Date,
        'Datetime' : DateTime,
        'String' : String(150),
        'Float' : Float,
        'Integer' : Integer
    }

    return type_mapping.get(type_str, String(150))

def get_table_from_yaml(yaml_file,metadata):

    with open(yaml_file, 'r') as f:
        schema = yaml.safe_load(f)
    
    columns = []

    table_name = list(schema.keys())[0]
    for dict_items in schema[table_name]:
        for column_name, column_type in dict_items.items():
            sql_type = get_type(column_type)
            columns.append(Column(column_name, sql_type))
    
    return Table(table_name, metadata, *columns)

def create_load_to_table(file_path,engine,df):
    metadata = MetaData()
    table = get_table_from_yaml(file_path,metadata)
    metadata.create_all(engine,checkfirst=True)
    df.to_sql(table.name, engine, if_exists='append', index=False)
    
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

