import os
import yaml
import json
import pandas as pd
from loguru import logger
from ELT.connectors.collisions_api import CollisionsApiClient

def load_dataset_ids(base_dir: str) -> list:
    """Load dataset ids from yaml file"""
    path_to_dataset_ids = os.path.join(base_dir, 'mvc.yaml')
    with open(path_to_dataset_ids, 'r') as f:
        return yaml.safe_load(f)
    

def get_since_iso(dir_path: str, key: str, env_start_date: str):
    """
    Fetch latest written date in iso format from json file if given.
    Otherwise use start date set in .env
    """
    files = os.listdir(dir_path)
    has_csv = any(f.endswith(".csv") for f in files)
    has_json = any(f.endswith(".json") for f in files)

    if has_csv and has_json:
        file_path_latest = os.path.join(dir_path, f"{key}_latest.json")
        with open(file_path_latest, "r") as f:
            latest_data = json.load(f)
        return latest_data.get("crash_date"), True
    else:
        return env_start_date, False
    

def fetch_collisions_latest(
        cac: CollisionsApiClient, dataset_id: str, since_iso: str, dir_path: str, key: str
        ) -> list:
    """
    Fetches the latest collision data from the NYC Collisions API since a given date and saves metadata.

    Args:
        cac (CollisionsApiClient): Authenticated API client used to fetch data.
        dataset_id (str): ID of the dataset to query from the NYC API.
        since_iso (str): ISO-formatted date string to filter records newer than this date.
        dir_path (str): Directory path where the metadata file should be saved.
        key (str): Identifier used to name the metadata file.

    Returns:
        list: A list of collision records (as dictionaries) fetched from the API.

    Side Effects:
        - If records are found, writes the latest crash date and time to a JSON file.
    """
    collected_data = cac.get_all_collisions_since(dataset_id, since_iso)
    if collected_data:
        crash_date = collected_data[0].get("crash_date")
        crash_time = collected_data[0].get("crash_time")
        if crash_date and crash_time:
            latest_path = os.path.join(dir_path, f"{key}_latest.json")
            with open(latest_path, "w") as f:
                json.dump({"crash_date": crash_date, "crash_time": crash_time}, f, indent=4)
            logger.info(f"Wrote latest crash date {crash_date[:10]} {crash_time} of {key} data to {latest_path}")
    return collected_data


def get_primary_key(yaml_file_path: str) -> str:
    """Get primary key from file"""
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data.get("primary_key")


def deduplicate_df(df: pd.DataFrame, metadata_yaml_file_path: str, key) -> pd.DataFrame:
    """
    Removes duplicate rows from the DataFrame based on the primary key defined in the metadata YAML.

    Args:
        df (pd.DataFrame): The DataFrame to deduplicate.
        metadata_yaml_file_path (str): Path to the YAML file containing table schema and primary key.
        key (str): Identifier for logging purposes (e.g., table name or dataset key).

    Returns:
        pd.DataFrame: A deduplicated DataFrame with only unique rows based on the primary key.
    """
    dedup_column = get_primary_key(metadata_yaml_file_path)
    df = df.drop_duplicates(subset=[dedup_column])
    logger.info(f"Deduplicated {key}: {len(df)} rows remaining after removing duplicates based on {dedup_column}")
    return df


def save_to_csv(
        df: pd.DataFrame, 
        file_path_csv: str, 
        incremental: bool, 
        metadata_yaml_file_path: str, 
        key: str
        ) -> None:
    """Saves a DataFrame to a CSV file, with optional incremental update logic."""
    if incremental and os.path.exists(file_path_csv):
        existing_df = pd.read_csv(file_path_csv)
        combined_df = pd.concat([df, existing_df], ignore_index=True)
        combined_df = deduplicate_df(
            combined_df, metadata_yaml_file_path=metadata_yaml_file_path, key=key
            )
        combined_df.to_csv(file_path_csv, index=False)
    else:
        df.to_csv(file_path_csv, index=False)
    logger.info(f"Saving {len(df)} rows to {file_path_csv}")
