from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.engine import URL
from sqlalchemy.dialects import postgresql
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    text,
    insert,
    select
)
from sqlalchemy.exc import SQLAlchemyError

class CollisionsDbClient:
    """
    A client for querying postgresql database.
    """

    def __init__(
        self,
        server_name: str,
        database_name: str,
        username: str,
        password: str,
        port: int = 5432
    ):
        """
        Initializes the database client with connection settings and creates a SQLAlchemy engine.

        Args:
            server_name (str): Hostname or IP address of the PostgreSQL server.
            database_name (str): Name of the target database.
            username (str): Database user name.
            password (str): Password for the database user.
            port (int, optional): Port number for the PostgreSQL server. Defaults to 5432.
        """
        self.host_name = server_name
        self.database_name = database_name
        self.username = username
        self.password = password
        self.port = port

        connection_url = URL.create(
            drivername="postgresql+pg8000",
            username=username,
            password=password,
            host=server_name,
            port=port,
            database=database_name
        )

        self.engine = create_engine(connection_url)

    def write_to_table(
        self, data: list[dict], table: Table, metadata: MetaData, batch_size: int = 100
        ) -> None:
        """
        Inserts or upserts a list of records into the specified PostgreSQL table.

        If a record conflicts on the primary key, it will be updated instead of inserted.
        The operation is performed in batches to reduce the risk of conflicts and improve performance.

        Args:
            data (list[dict]): List of records to insert or upsert.
            table (Table): SQLAlchemy Table object representing the target table.
            metadata (MetaData): SQLAlchemy MetaData object used to create the table if it doesn't exist.
            batch_size (int): Number of records to insert per batch. Default is 100.
        """
        key_columns = [
            pk_column.name for pk_column in table.primary_key.columns.values()
        ]
        metadata.create_all(self.engine)  # creates table if it does not exist
        try:
            with self.engine.connect() as conn:
                for i in range(0, len(data), batch_size):
                    batch = data[i : i + batch_size]

                    insert_stmt = postgresql.insert(table).values(batch)
                    upsert_stmt = insert_stmt.on_conflict_do_update(
                        index_elements=key_columns,
                        set_={
                            c.key: c for c in insert_stmt.excluded if c.key not in key_columns
                        },
                    )

                    conn.execute(upsert_stmt)
                conn.commit()

        except SQLAlchemyError as e:
            print(f"Error while writing to table: {e}")
            raise


    def drop_table(self, table_name: str):
        """
        Drops a table from the database if it exists.
        Useful for test cleanup.
        """
        with self.engine.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
            conn.commit()


    def insert(self, data: list[dict], table, metadata):
        """
        Insert a list of dictionaries into the specified table. For testing.
        """
        metadata.create_all(self.engine)

        with self.engine.connect() as conn:
            stmt = insert(table).values(data)
            conn.execute(stmt)
            conn.commit()


    def select_all(self, table):
        """
        Select all rows from the specified table.
        Returns a list of dictionaries. For testing
        """
        with self.engine.connect() as conn:
            stmt = select(table)
            result = conn.execute(stmt)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]