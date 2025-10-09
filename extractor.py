import os
import pandas as pd
import requests
from datetime import datetime
from loguru import logger
from config import APIConfig

class APIExtractor:

    def __init__(self,config # <- pass in APIConfig object
                 ,base_dir):

        self.config = config
        self.base_dir = base_dir
    
    def _build_request_params(self,query):

        headers = self.config.get_headers()
        params = {'$query':query}
        
        return self.config.base_url,headers,params
    
    def _get_raw_data_path(self,subset,date):

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        directory_path = os.path.join(self.base_dir, 'raw_data', subset)
        os.makedirs(directory_path, exist_ok=True)
        return os.path.join(directory_path, f"{date}_{subset}_{timestamp}.csv")
    
    def _cleanup_old_files(self,directory_path,date):

        if not os.path.exists(directory_path):
            return

        try: 
            for filename in os.listdir(directory_path):
                if date in filename:
                    old_file = os.path.join(directory_path, filename)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        logger.info(f"Removed old file: {old_file}")
                        break
        except FileNotFoundError:
            logger.error(f"Error: File '{old_file}' not found.")
    
    def save_to_csv(self, df, subset, date):

        directory_path = os.path.join(self.base_dir, 'raw_data', subset)
        self._cleanup_old_files(directory_path, date)
        
        try:
            file_path = self._get_raw_data_path(subset, date)
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {len(df)} rows to {file_path}")
        except Exception as e:
            logger.error(f"An unexpected error occured!:{e}")
    
    def extract_data(self,url,subset,date):

        self.config.base_url = url
        query = f"SELECT * WHERE crash_date='{date}'"
        base_url, params, headers = self._build_request_params(query)
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Extracting data for {subset} on {date}")
            df = pd.json_normalize(response.json())
            self.save_to_csv(df, subset, date)
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting data: {e}")
            return None
    
    def get_latest_date(self, url):

        self.config.base_url = url
        query = "SELECT * ORDER BY crash_date DESC LIMIT 1"
        base_url, params, headers = self._build_request_params(query)
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            df = pd.json_normalize(response.json())
            return pd.to_datetime(df['crash_date']).dt.date[0]
            
        except Exception as e:
            logger.error(f"Error getting latest date: {e}")
            return None