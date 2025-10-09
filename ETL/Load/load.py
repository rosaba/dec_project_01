from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, Float, Date, DateTime, Time, UUID
import pandas as pd
from connectors.collisions_db import CollisionsDbClient
import yaml


def load(
    df: pd.DataFrame,
    collisions_db_client: CollisionsDbClient,
    table: Table,
    metadata: MetaData,
) -> None:
    """Load dataframe to a database."""

    collisions_db_client.write_to_table(
        data=df.to_dict(orient="records"), table=table, metadata=metadata
    )

def get_type(type_str: str) -> type:

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

def get_table_from_yaml(metadata_yaml_file_path: str, metadata: MetaData) -> Table:

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
    return [
        col.name
        for col in table.columns
        if isinstance(col.type, Integer)
    ]

def clean_integer_columns(df: pd.DataFrame, table: Table) -> pd.DataFrame:
    for col in table.columns:
        if isinstance(col.type, Integer) and col.name in df.columns:
            df[col.name] = pd.to_numeric(df[col.name], errors='coerce')  # float -> int, bad -> NaN
            df[col.name] = df[col.name].astype('Int64')  # nullable integer type (NaNs allowed)
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


def create_load_to_table(metadata_yaml_file_path: str, client: CollisionsDbClient, df: pd.DataFrame) -> None:
    metadata = MetaData()
    table = get_table_from_yaml(metadata_yaml_file_path, metadata)
    df = convert_nan_to_null(df)

    for col in table.columns:
        if isinstance(col.type, Integer) and col.name in df.columns:
            bad_vals = df[~df[col.name].astype(str).str.match(r"^-?\d+$")][col.name].unique()
            if len(bad_vals) > 0:
                print(f"⚠️ Non-integer values in column '{col.name}': {bad_vals}")

    df = clean_integer_columns(df=df, table=table)
    
    load(df=df, collisions_db_client=client, table=table, metadata=metadata)




"""
insert_statement = postgresql.insert(crashes_table).values(df_crashes.to_dict(orient='records'))
upsert_statement = insert_statement.on_conflict_do_update(
    index_elements=['id', 'exchange', 'timestamp'],
    set_={c.key: c for c in insert_statement.excluded if c.key not in ['id', 'exchange', 'timestamp']})
engine.execute(upsert_statement)




meta = MetaData()

crashes_table = Table(
    "vehicle_collisions",
    meta,
    Column("collision_id", Integer, primary_key=True),
    Column("crash_date", Date),
    Column("crash_time", Time),
    Column("borough", String),
    Column("zip_code", String),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("on_street_name", String),
    Column("number_of_persons_injured", Integer),
)


#def upsert_collisions(df, engine):
    # Create the table if it doesn't exist
   # meta.create_all(engine)

    # Convert DataFrame to list of dicts
 #   records = df.to_dict(orient="records")

    # Build insert statement
 #   insert_statement = insert(crashes_table).values(records)

    # Build upsert (ON CONFLICT DO UPDATE)
   # upsert_statement = insert_statement.on_conflict_do_update(
  #      index_elements=["collision_id"],
  #      set_={
  #          c.key: c
   #         for c in insert_statement.excluded
  #          if c.key != "collision_id"
   #     }
   # )

    # Execute
   # engine.execute(upsert_statement)

#engine = create_engine()
#upsert_collisions(df, engine)
"""