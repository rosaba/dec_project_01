import pandas as pd
import requests
import yaml
import os

yaml_file = 'mvc.yaml'

with open(yaml_file, 'r') as f:
    mvc_data = yaml.load(f, Loader=yaml.FullLoader)

def get_crashes_data(
        base_url, 
        offset=0, #by default the API limit is 1000 per request, so we use offset to 'page' through the data
        date='2012-07-01' #hardcoding it for now, need to figure out how to dynamically get the earliest data point
        ):
    url = base_url
    params = {
    "$limit" : 1000,
    "$offset" : offset,
    "crash_date" : date
    }
    crashes_df = pd.json_normalize(requests.get(url, params = params).json())
    file_path =f'./raw_data/crashes/{date}_crashes.csv' ##saving by date to seperate folders, 
                                #we will have to choose between saving to csv first or direct upload to postgres

    if not os.path.exists(file_path):
        crashes_df.to_csv(file_path, index=False, mode='a', header=True)
    else:
        crashes_df.to_csv(file_path, index=False, mode='a', header=False)
    