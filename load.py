from sqlalchemy.engine import URL
from sqlalchemy import create_engine, inspect, text, Table, Column, MetaData, Integer, String, Float, Date, DateTime
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os
import psycopg2
import yaml
from loguru import logger
from datetime import timedelta
from extract import get_data

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
        'String' : String(250),
        'Float' : Float,
        'Integer' : Integer
    }

    return type_mapping.get(type_str, String(150))

def get_table_from_yaml(yaml_file,metadata):

    with open(yaml_file, 'r') as f:
        schema = yaml.safe_load(f)
    primary_key_column = schema['primary_key']
    columns = []

    table_name = list(schema.keys())[0]
    for dict_items in schema[table_name]:
        for column_name, column_type in dict_items.items():
            sql_type = get_type(column_type)
            is_primary = (column_name == primary_key_column)

            columns.append(Column(column_name, sql_type,primary_key = is_primary))
    
    return Table(table_name, metadata, *columns)

def create_load_to_table(file_path,engine,df):
    metadata = MetaData()
    table = get_table_from_yaml(file_path,metadata)
    metadata.create_all(engine,checkfirst=True)
    df.to_sql(table.name, engine, if_exists='append', index=False)

def upsert_to_db(table_name,url,engine, latest_db_date):
    metadata = MetaData()
    metadata.reflect(bind=engine, only=[table_name])
    table = metadata.tables[table_name]
    conflict_columns = [col.name for col in table.primary_key.columns]
    current_date = latest_db_date
    while current_date>=(latest_db_date - timedelta(days=3)):
        logger.info(f'Processing date: {current_date}')
        api_df = get_data(url,table_name,current_date)
        with engine.begin() as connection:
            for _, row in api_df.iterrows():
                row_dict = row.to_dict()

                stmt = insert(table).values(row_dict)
                
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_={
                        col: stmt.excluded[col] 
                        for col in row_dict.keys() 
                        if col not in conflict_columns
                    }
                )
                
                connection.execute(stmt)
        current_date-=timedelta(days=1)


    
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

