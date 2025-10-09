from extract import *
from load import *
from datetime import datetime, timedelta, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(BASE_DIR, 'mvc.yaml')

load_dotenv()
username = os.environ.get('DESTINATION_DB_USERNAME')
password = os.environ.get('DESTINATION_DB_PASSWORD')
host = os.environ.get('DESTINATION_SERVER_NAME')
port = os.environ.get('DESTINATION_PORT')
database = os.environ.get('DESTINATION_DATABASE_NAME')

source_url = create_db_url(username, password, host, port, database)

with open(yaml_path, 'r') as f:
    mvc_data = yaml.load(f, Loader=yaml.FullLoader)

if check_connection(source_url):
    engine = create_engine(source_url)
    inspector = inspect(engine)
    for key in mvc_data.keys():
        latest_api_date = get_date(mvc_data[key],'SELECT * ORDER BY crash_date DESC LIMIT 1')

        if f'{key}' not in inspector.get_table_names():
            latest_db_date = latest_api_date - timedelta(years=2) # <- first time upload, need to refactor to data from previous 90 days dynamically
        else:
            date_query = f'SELECT MAX(crash_date) from {key}'
            logger.info("Updating data for the past 30 days")
            with engine.connect() as connection:
                latest_db_date = connection.execute(text(date_query)).scalar() # <- subsequent uploads
                metadata = MetaData()
                metadata.reflect(bind=engine, only=[key])
                table = metadata.tables[key]
                conflict_columns = [col.name for col in table.primary_key.columns]
                current_date = latest_db_date
                while current_date>(latest_db_date - timedelta(days=30)):
                    upsert_to_db(key,mvc_data[key],engine,current_date,table,conflict_columns)
                    current_date-=timedelta(days=1)

        looping_date = latest_api_date # < - new data upload
        logger.info("Uploading new data to database")
        while looping_date>latest_db_date:
            df = get_data(mvc_data[key], key, looping_date)
            save_to_csv(df,key,looping_date)
            create_load_to_table(f'./{key}_metadata.yaml',engine,df)
            looping_date-=timedelta(days=1)
        
        
else:
    print("Please check connection")
        