import yaml
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect, text, Table, Column, MetaData
from sqlalchemy import Integer, String, Float, Date, DateTime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from loguru import logger
from config import DatabaseConfig

def get_sqlalchemy_type(type_str):
    
    type_mapping = {
        'Date': Date,
        'Datetime': DateTime,
        'String': String(250),
        'Float': Float,
        'Integer': Integer
    }
    return type_mapping.get(type_str, String(250))

def load_table_from_yaml(yaml_file, metadata):

    with open(yaml_file, 'r') as f:
        schema = yaml.safe_load(f)
    
    primary_key_column = schema.get('primary_key')
    columns = []
    
    table_name = list(schema.keys())[0]
    
    for dict_items in schema[table_name]:
        for column_name, column_type in dict_items.items():
            sql_type = get_sqlalchemy_type(column_type)
            is_primary = (column_name == primary_key_column)
            columns.append(Column(column_name, sql_type, primary_key=is_primary))
    
    return Table(table_name, metadata, *columns)

def convert_nan_to_null(df):

    df = df.replace({
        np.nan: None,
        pd.NA: None,
        pd.NaT: None,
        'nan': None,
        'NaN': None,
        'NAN': None,
        'None': None,
        '': None
    })
    
    df = df.where(pd.notna(df), None)
    return df

class DatabaseLoader:

    def __init__(self,config# <- add DatabaseConfig object
                 ):
        self.config = config
        self.engine = None
        self.inspector = None
    
    def connect(self):

        try:
            url = self.config.create_url()
            self.engine = create_engine(url)
            
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            self.inspector = inspect(self.engine)
            logger.info("Database connection established")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def table_exists(self, table_name):
        
        return table_name in self.inspector.get_table_names()
    
    def get_max_date(self, table_name, date_column='crash_date'):
        
        query = f'SELECT MAX({date_column}) FROM {table_name}'
        
        with self.engine.connect() as connection:
            return connection.execute(text(query)).scalar()
    
    def get_primary_key_columns(self, table_name):

        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=[table_name])
        table = metadata.tables[table_name]
        return [col.name for col in table.primary_key.columns]
    
    def create_table_from_yaml(self, yaml_file, df):

        metadata = MetaData()
        table = load_table_from_yaml(yaml_file, metadata)
        metadata.create_all(self.engine, checkfirst=True)
        
        cleaned_df = convert_nan_to_null(df)
        cleaned_df.to_sql(table.name, self.engine, if_exists='append', index=False)
        logger.info(f"Created and loaded table: {table.name}")
    
    def upsert_data(self, table_name, df, conflict_columns):

        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=[table_name])
        table = metadata.tables[table_name]
        
        cleaned_df = convert_nan_to_null(df)
        
        with self.engine.begin() as connection:
            for _, row in cleaned_df.iterrows():
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
        
        logger.info(f"Upserted {len(cleaned_df)} rows into {table_name}")
    
    def close(self):

        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")