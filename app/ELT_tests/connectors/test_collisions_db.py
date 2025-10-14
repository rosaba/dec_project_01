from dotenv import load_dotenv
import pytest
import os
from ELT.connectors.collisions_db import CollisionsDbClient
from sqlalchemy import Table, Column, Integer, String, MetaData

@pytest.fixture
def setup_collisions_db_client():
    load_dotenv()
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    PORT = os.environ.get("PORT")

    collisions_db_client = CollisionsDbClient(
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        port=PORT,
    )
    return collisions_db_client


@pytest.fixture
def setup_table():
    table_name = "test_table"
    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", String),
    )
    return table_name, table, metadata


def test_collisions_db_client_insert(setup_collisions_db_client, setup_table):
    setup_collisions_db_client = setup_collisions_db_client
    table_name, table, metadata = setup_table
    setup_collisions_db_client.drop_table(table_name)

    data = [{"id": 1, "value": "crash"}, {"id": 2, "value": "vehicle"}, {"id": 3, "value": "person"}]

    setup_collisions_db_client.insert(data=data, table=table, metadata=metadata)

    result = setup_collisions_db_client.select_all(table=table)
    assert len(result) == 3

    setup_collisions_db_client.drop_table(table_name)