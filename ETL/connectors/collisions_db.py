from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.engine import URL
from sqlalchemy.dialects import postgresql
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
)
from sqlalchemy.dialects import postgresql
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
        self, data: list[dict], table: Table, metadata: MetaData, batch_size: int = 100) -> None:
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