"""
Data loading module for NYC Motor Vehicle Collisions.

This module handles database connections, table creation, data transformation,
and loading data into PostgreSQL database.
"""

from sqlalchemy.engine import URL
from sqlalchemy import create_engine, inspect, text, Table, Column, MetaData, Integer, String, Float, Date, DateTime
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os
import yaml
from loguru import logger
from datetime import timedelta
from extract import get_data, save_to_csv
import numpy as np
import pandas as pd

def create_db_url(username, password, host, port, database) ->  URL:
    """
    Create SQLAlchemy database URL for PostgreSQL connection.
    
    Args:
        username (str): Database username
        password (str): Database password
        host (str): Database host address
        port (int): Database port number
        database (str): Database name
    
    Returns:
        sqlalchemy.engine.URL: Database connection URL object
    """

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
    """
    Test database connection.
    
    Args:
        source_connection_url (sqlalchemy.engine.URL): Database URL to test
    
    Returns:
        bool: True if connection successful
        str: Error message if connection fails
    """

    try:
        source_engine = create_engine(source_connection_url)
        with source_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        return f'{e}'

def get_type(type_str):
    """
    Map string type names to SQLAlchemy column types.
    
    Args:
        type_str (str): Type name ('Date', 'Datetime', 'String', 'Float', 'Integer')
    
    Returns:
        sqlalchemy type: Corresponding SQLAlchemy column type
    """

    type_mapping = {
        'Date' : Date,
        'Datetime' : DateTime,
        'String' : String(250),
        'Float' : Float,
        'Integer' : Integer
    }

    return type_mapping.get(type_str, String(150))

def get_table_from_yaml(yaml_file,metadata):
    """
    Create SQLAlchemy Table object from YAML schema definition.
    
    Args:
        yaml_file (str): Path to YAML file containing table schema
        metadata (sqlalchemy.MetaData): SQLAlchemy metadata object
    
    Returns:
        sqlalchemy.Table: Table object with defined columns and primary key
    """

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
    """
    Create table from YAML schema and load DataFrame data into it.
    
    Args:
        file_path (str): Path to YAML schema file
        engine (sqlalchemy.engine.Engine): Database engine
        df (pd.DataFrame): DataFrame to load into table
    
    Returns:
        None
    """

    metadata = MetaData()
    table = get_table_from_yaml(file_path,metadata)
    metadata.create_all(engine,checkfirst=True)
    df.to_sql(table.name, engine, if_exists='append', index=False)

def convert_nan_to_null(df):
    """
    Convert all NaN, NA, and empty values to None (SQL NULL).
    
    Handles numpy NaN, pandas NA/NaT, string representations of NaN,
    and empty strings.
    
    Args:
        df (pd.DataFrame): DataFrame to clean
    
    Returns:
        pd.DataFrame: DataFrame with NaN values replaced by None
    """

    df = df.replace({
        np.nan: None,
        pd.NA: None,
        pd.NaT: None
    })
    
    df = df.where(pd.notna(df), None)
    
    df = df.replace({
        'nan': None,
        'NaN': None,
        'NAN': None,
        'None': None,
        '': None
    })
    
    return df

def upsert_to_db(table_name,url,engine, current_date, table, conflict_columns):
    """
    Insert or update data in database for a specific date.
    
    Fetches data from API, cleans it, and performs upsert operation
    (insert new records or update existing ones on conflict).
    
    Args:
        table_name (str): Name of the database table
        url (str): API endpoint URL
        engine (sqlalchemy.engine.Engine): Database engine
        current_date (datetime.date): Date to process
        table (sqlalchemy.Table): Table object
        conflict_columns (list): Column names that define uniqueness for conflict resolution
    
    Returns:
        None
    """

    logger.info(f'Processing date: {current_date}')
    api_df = get_data(url,table_name,current_date)
    api_df = convert_nan_to_null(api_df)
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



