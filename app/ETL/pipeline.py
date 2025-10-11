import os
from ETL.connectors.collisions_api import CollisionsApiClient
import pandas as pd
from dotenv import load_dotenv
from ETL.Extract.extract import load_dataset_ids, get_since_iso, fetch_collisions_latest, save_to_csv, deduplicate_df
from loguru import logger
from ETL.connectors.collisions_db import CollisionsDbClient
from ETL.Load.load import prep_and_load_table


def main():

    load_dotenv()

    X_APP_TOKEN = os.environ.get("X-App-Token")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    PORT = os.environ.get("PORT")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    dataset_ids = load_dataset_ids(BASE_DIR)

    # Extract (either full at first time or incremental afterwards)

    cac = CollisionsApiClient(app_token=X_APP_TOKEN)

    for key in dataset_ids.keys():

        dir_path = os.path.join(BASE_DIR, 'raw_data', key)

        since_iso, incremental = get_since_iso(dir_path=dir_path, key=key, env_start_date=os.environ.get("start_date_iso"))

        collected_data = fetch_collisions_latest(cac=cac, dataset_id=dataset_ids[key], since_iso=since_iso, dir_path=dir_path, key=key)

        if collected_data:
            file_path_csv = os.path.join(dir_path, f"{key}.csv")
            df = pd.json_normalize(collected_data)
            file_path_metadata = os.path.join(BASE_DIR, 'Load/metadata', f"{key}_metadata.yaml")
            save_to_csv(
                df=df, file_path_csv=file_path_csv, incremental=incremental, metadata_yaml_file_path=file_path_metadata, key=key
                )
        else:
            logger.info(f"No fresh data that could be collected for {key} dataset")


    # Load (with upsert)
    collisions_db_client = CollisionsDbClient(
        server_name=SERVER_NAME,
        database_name=DATABASE_NAME,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        port=PORT,
    )

    for key in dataset_ids.keys():
        file_path_metadata = os.path.join(BASE_DIR, 'Load/metadata', f"{key}_metadata.yaml")
        file_path_csv = os.path.join(BASE_DIR, 'raw_data', key, f"{key}.csv")
        df = pd.read_csv(file_path_csv)
        prep_and_load_table(metadata_yaml_file_path=file_path_metadata, client=collisions_db_client, df=df)


    # Transform
    
if __name__ == '__main__':
    main()