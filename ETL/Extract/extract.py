import os
import yaml
import json
import pandas as pd
from loguru import logger
from connectors.collisions_api import CollisionsApiClient

def load_dataset_ids(base_dir: str) -> list:
    path_to_dataset_ids = os.path.join(base_dir, 'mvc.yaml')
    with open(path_to_dataset_ids, 'r') as f:
        return yaml.safe_load(f)
    

def get_since_iso(dir_path: str, key: str, env_start_date: str):
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
    

def fetch_collisions_latest(cac: CollisionsApiClient, dataset_id: str, since_iso: str, dir_path: str, key: str) -> list:
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


def save_to_csv(df: pd.DataFrame, file_path_csv: str, incremental: bool) -> None:
    if incremental and os.path.exists(file_path_csv):
        existing_df = pd.read_csv(file_path_csv)
        combined_df = pd.concat([df, existing_df], ignore_index=True)
        combined_df.to_csv(file_path_csv, index=False)
    else:
        df.to_csv(file_path_csv, index=False)
    logger.info(f"Saving {len(df)} rows to {file_path_csv}")
