import pandas as pd
import requests
import yaml
import os
from dotenv import load_dotenv

def get_data_response(url:str, subset, limit:int, offset:int):
    load_dotenv()

    base_url = url

    headers = {
        'X-App-Token': os.environ.get("X-APP-TOKEN"),

    }

    params = {
            '$query': f'SELECT * ORDER BY crash_date ASC LIMIT {limit} OFFSET {offset}',
        }
    
    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        df = pd.json_normalize(response.json())

        file_path = f'./raw_data/{subset}/{subset}.csv'
        df.to_csv(file_path, index=False)

        print(f"✓ Saved {len(df)} rows to {file_path}")
    else:
        print(f"Error - {response.status_code}, please check configuration!")



def main():

    with open('./mvc.yaml', 'r') as f:
        mvc_data = yaml.load(f, Loader=yaml.FullLoader)

    for key in mvc_data.keys():
        get_data_response(mvc_data[key], key, 1000,0)


if __name__ == '__main__':
    main()