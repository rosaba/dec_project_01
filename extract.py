import pandas as pd
import requests
import yaml
import os
from dotenv import load_dotenv
from datetime import datetime
from loguru import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def request_config(url,param):
    load_dotenv()
    base_url = url

    headers = {'X-App-Token': os.environ.get("X-APP-TOKEN")}

    params = {'$query': param} 

    return base_url, params, headers

def save_to_csv(df, subset, date):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory_path = os.path.join(BASE_DIR,'raw_data', subset)
    file_path = os.path.join(directory_path, f"{date}_{subset}_{timestamp}.csv")

    for filename in os.listdir(directory_path):
        if f'{date}' in filename:
            old_file = os.path.join(directory_path, filename)
            if os.path.exists(old_file):
                os.remove(old_file)
                break
            else:
                print(f'{old_file} not found during deletion attempt')

    df.to_csv(file_path, index=False)
    logger.info(f"Saving {len(df)} rows to {file_path}")

def get_data(url:str, subset, date):
    
    base_url, params, headers = request_config(url,f'SELECT * WHERE crash_date=\'{date}\'')
    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        logger.info(f"Extracting data for {subset}")
        df = pd.json_normalize(response.json())
        save_to_csv(df,subset,date)
        return df

    else:
        logger.error(f"Error - {response.status_code}, please check configuration!")


def get_date(url,query):
    base_url, params, headers = request_config(url,query)
    response = requests.get(base_url, params=params, headers=headers)

    df = pd.json_normalize(response.json())
    return pd.to_datetime(df['crash_date']).dt.date[0]

