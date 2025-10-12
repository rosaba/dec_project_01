
from pathlib import Path
from auth.API_auth import api_Authentication
from extractor.api_extractor import api_extractor
from Utils import config_parser
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from loader.DB_loader import db_loader
from auth.DB_auth import DB_auth
import re
from sqlalchemy import MetaData, Table, Column, String, Integer, Date, DateTime, inspect, Float
from Utils.logger import setup_logger

logger = setup_logger()

config_data =  config_parser.extract_config()
Base_dir = Path(__file__).parent.parent


class pipeline():
    def __init__(self,config):
        self.config = config
    


    def check_file_path(path:str):
        if os.path.exists(path):
            return True
    
    def _get_max_date_from_api(self, base_url, params, query = None) -> str:
        extractor = api_extractor( base_url, params, query= None)
        data = extractor.extract()
        max_date = data.iloc[0, 0]
        if isinstance(max_date, str):
            max_date = pd.to_datetime(max_date).date()

    # Return as formatted SQL-friendly string
            return max_date.strftime("%Y-%m-%d")
        return max_date
    
    def run_etl(self, base_dir: Path, engine):
        for k, v in self.config['base_url'].items():
            file_path = base_dir / self.config['file_name'][k]

        # Extraction_Incrmental_Format
            if not file_path.exists():
                logger.info("Extracting First Time Load")
                params = self.config['first_time_load']
                print (params)
            else:
                logger.info("Extracting incremental data")
                max_date = self._get_max_date_from_api(base_url=v, params=self.config['max_date_data'])
                select_part = self.config['incremental_query']['query']['Select']
                where_template = self.config['incremental_query']['query']['Where']
                where_clause = where_template.replace("{max_date}", f"'{max_date}'")
                params = {"query": f"SELECT {select_part} WHERE {where_clause}"}
            extractor = api_extractor(base_url=v, params=params, query=None)
            data_for_table = extractor.extract()
            data_for_table.columns = [c.replace(":", "").replace(".", "_") for c in data_for_table.columns]


        # Clean data
            invalid_values = {"": None, " ": None, "NULL": None, "NaN": None, "n/a": None, "N/A": None}
            data_for_table = data_for_table.replace(invalid_values)
            data_for_table = data_for_table.where(pd.notnull(data_for_table), None)    

        # Save raw
            data_for_table.to_csv(file_path, index=False)

        # Load_Upsert
            table = db_loader(k, self.config['tables'][k]['columns']).create_metadata()
            data_for_table_json = data_for_table.to_dict(orient="records")

            logger.info("Upserting data")
            stmt = insert(table).values(data_for_table_json)
            upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[i['name'] for i in self.config['tables'][k]['columns'] if i.get('primary_key', False)],
            set_={i['name']: stmt.excluded[i['name']] for i in self.config['tables'][k]['columns'] if not i.get('primary_key', False)}
        )

            with engine.begin() as conn:
                conn.execute(upsert_stmt)
            print(f"Table {k} inserted/updated successfully.")



if __name__ == "__main__":
    engine = DB_auth().create_engine()
    p = pipeline(config= config_data)
    p.run_etl(Base_dir, engine=engine)


