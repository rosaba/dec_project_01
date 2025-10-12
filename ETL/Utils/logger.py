from loguru import logger
from datetime import date

today = date.today()



def setup_logger():
    logger.add(f"ETL/logs/etl{today}", rotation ="1 MB", level="INFO")
    return logger



