import os
import yaml
from datetime import timedelta
from loguru import logger
from config.config import APIConfig, DatabaseConfig
from extract.extractor import APIExtractor
from load.loader import DatabaseLoader


class ETLPipeline:

    
    def __init__(self, base_dir, yaml_config_path):

        self.base_dir = base_dir
        self.yaml_config_path = yaml_config_path
        
        self.api_config = APIConfig()
        self.db_config = DatabaseConfig()
        
        self.extractor = APIExtractor(self.api_config, base_dir)
        self.loader = DatabaseLoader(self.db_config)
        
        self.data_sources = self._load_data_sources()
    
    def _load_data_sources(self):

        with open(self.yaml_config_path, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    def _process_new_data(self, source_name, url, latest_api_date, latest_db_date):

        logger.info(f"Uploading new data for {source_name}")
        current_date = latest_api_date
        yaml_metadata = f'./{source_name}_metadata.yaml'
        
        while current_date > latest_db_date:
            df = self.extractor.extract_data(url, source_name, current_date)
            
            if df is not None and not df.empty:
                self.loader.create_table_from_yaml(yaml_metadata, df)
            
            current_date -= timedelta(days=1)
    
    def _update_recent_data(self, source_name, url, latest_db_date, days=30):

        logger.info(f"Updating data for the past {days} days for {source_name}")
        
        conflict_columns = self.loader.get_primary_key_columns(source_name)
        current_date = latest_db_date
        end_date = latest_db_date - timedelta(days=days)
        
        while current_date > end_date:
            df = self.extractor.extract_data(url, source_name, current_date)
            
            if df is not None and not df.empty:
                self.loader.upsert_data(source_name, df, conflict_columns)
            
            current_date -= timedelta(days=1)
    
    def _process_data_source(self, source_name, url):

        logger.info(f"Processing data source: {source_name}")
        
        # Get latest date from API
        latest_api_date = self.extractor.get_latest_date(url)
        if latest_api_date is None:
            logger.error(f"Could not get latest date for {source_name}")
            return
        
        # Determine latest date in database
        if not self.loader.table_exists(source_name):
            # First time upload - load 2 years of data
            logger.info(f"Table {source_name} does not exist. Creating new table.")
            latest_db_date = latest_api_date - timedelta(days=730)
        else:
            # Subsequent uploads
            logger.info(f"Starting update of old data and upload of new to Table {source_name}")
            latest_db_date = self.loader.get_max_date(source_name)
            
            # Update recent data to handle late arrivals
            if latest_db_date:
                self._update_recent_data(source_name, url, latest_db_date)
        
        # Process new data
        self._process_new_data(source_name, url, latest_api_date, latest_db_date)
        
        logger.info(f"Completed processing {source_name}")
    
    def run(self):

        logger.info("Starting ETL pipeline")
        
        if not self.loader.connect():
            logger.error("Could not connect to database. Exiting.")
            return False
        
        try:
            for source_name, url in self.data_sources.items():
                self._process_data_source(source_name, url)
            
            logger.info("ETL pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False
            
        finally:
            self.loader.close()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(base_dir, 'mvc.yaml')
    
    pipeline = ETLPipeline(base_dir, yaml_path)
    pipeline.run()