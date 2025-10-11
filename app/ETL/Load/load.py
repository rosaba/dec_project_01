from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, Float, Date, DateTime, Time, UUID
import pandas as pd
from ETL.connectors.collisions_db import CollisionsDbClient
import yaml
from loguru import logger


def load(
    df: pd.DataFrame,
    collisions_db_client: CollisionsDbClient,
    table: Table,
    metadata: MetaData,
) -> None:
    """Load dataframe to a database."""

    collisions_db_client.write_to_table(
        data=df.to_dict(orient="records"), table=table, metadata=metadata, batch_size=100
    )

def get_type(type_str: str) -> type:
    """Maps a string representation of a SQL data type to its corresponding SQLAlchemy type."""

    type_mapping = {
        'Date' : Date,
        'Datetime' : DateTime,
        'Time': Time,
        'String(10)' : String(10),
        'String(50)': String(50),
        'UUID': UUID,
        'Float' : Float,
        'Integer' : Integer,
        'BigInteger': BigInteger
    }

    return type_mapping.get(type_str, String(150))

def get_table(metadata_yaml_file_path: str, metadata: MetaData) -> Table:
    """
    Constructs a SQLAlchemy Table object from a YAML metadata file.

    Args:
        metadata_yaml_file_path (str): Path to the YAML file defining the schema.
        metadata (MetaData): SQLAlchemy MetaData object to bind the table to.

    Returns:
        sqlalchemy.Table: The constructed Table object with columns and primary key.
    """

    with open(metadata_yaml_file_path, 'r') as f:
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


def get_integer_columns(table: Table) -> list:
    """Get columns of type Integer"""
    return [
        col.name
        for col in table.columns
        if isinstance(col.type, Integer)
    ]


def clean_integer_columns(df: pd.DataFrame, table: Table) -> pd.DataFrame:
    """Ensures all integer columns in the DataFrame are properly typed and clean."""
    for col in table.columns:
        if isinstance(col.type, Integer) and col.name in df.columns:
            df[col.name] = pd.to_numeric(df[col.name], errors='coerce')
            df[col.name] = df[col.name].astype('Int64')
    return df


def convert_nan_to_null(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces NaN, NaT, pd.NA and common string placeholders with None.
    Avoids replacing valid data.
    """
    common_nulls = {'nan', 'NaN', 'NAN', 'null', 'NULL', 'None', '', 'n/a', 'N/A', '-'}

    def clean_value(val):
        # If it's already a known missing value (NaN, pd.NA, etc.)
        if pd.isna(val):
            return None

        # If it's a list with a single null-like value, flatten it
        if isinstance(val, list) and len(val) == 1:
            val = val[0]

        # If it's a string and matches a known null representation
        if isinstance(val, str) and val.strip() in common_nulls:
            return None

        return val

    # Apply to every column, value by value
    for col in df.columns:
        df[col] = df[col].apply(clean_value)

    return df


def prep_and_load_table(
        metadata_yaml_file_path: str, client: CollisionsDbClient, df: pd.DataFrame
        ) -> None:
    """Processes and loads a DataFrame into a PostgreSQL table."""
    metadata = MetaData()
    table = get_table(metadata_yaml_file_path, metadata)
    df = convert_nan_to_null(df)

    for col in table.columns:
        if isinstance(col.type, Integer) and col.name in df.columns:
            bad_vals = df[~df[col.name].astype(str).str.match(r"^-?\d+$")][col.name].unique()
            if len(bad_vals) > 0:
                logger.warning(f"Non-integer values in column '{col.name}': {bad_vals}")

    df = clean_integer_columns(df=df, table=table)
    
    load(df=df, collisions_db_client=client, table=table, metadata=metadata)