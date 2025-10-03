import pandas as pd
import requests
import yaml
import os
from dotenv import load_dotenv

yaml_file = 'mvc.yaml'

with open(yaml_file, 'r') as f:
    mvc_data = yaml.load(f, Loader=yaml.FullLoader)

def get_data(base_url, row_size=1000, datapage=1):

    url = base_url

    headers = {
        'X-App-Token': os.environ.get("X-APP-TOKEN")
    }

    payload = {
        'query': 'SELECT * ORDER BY crash_date ASC',
        'page': {
            'pageNumber': datapage,
            'pageSize': row_size
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        crashes_df = pd.json_normalize(requests.json())

    file_path =f'./raw_data/crashes/pg_{datapage}_crashes.csv'

    if not os.path.exists(file_path):
        crashes_df.to_csv(file_path, index=False, mode='a', header=True)
    else:
        crashes_df.to_csv(file_path, index=False, mode='a', header=False)
    