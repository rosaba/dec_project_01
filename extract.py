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

def get_data(url:str, subset, date, limit:int, offset:int):
    
    base_url, params, headers = request_config(url,f'SELECT * WHERE crash_date=\'{date}\' LIMIT {limit} OFFSET {offset}')
    
    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        df = pd.json_normalize(response.json())
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        file_path = os.path.join(BASE_DIR, 'raw_data', subset, f"{date}_{subset}_{timestamp}.csv")

        df.to_csv(file_path, index=False)
        logger.info(f"Saving {len(df)} rows to {file_path}")

    else:
        logger.error(f"Error - {response.status_code}, please check configuration!")

def get_date(url,query):
    base_url, earlist_params, headers = request_config(url,query)
    response = requests.get(base_url, params=earlist_params, headers=headers)

    df = pd.json_normalize(response.json())
    return pd.to_datetime(df['crash_date']).dt.date[0]

#latest_date_query = 'SELECT * ORDER BY crash_date DESC LIMIT 1 '
def main():
    #BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(BASE_DIR, 'mvc.yaml')

    with open(yaml_path, 'r') as f:
        mvc_data = yaml.load(f, Loader=yaml.FullLoader)

    for key in mvc_data.keys():
        date = get_date(mvc_data[key],'SELECT * ORDER BY crash_date DESC LIMIT 1')
        get_data(mvc_data[key], key, date, 1000,0)
    
if __name__ == '__main__':
    main()