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
            latest_db_date = date(2025, 7, 31) # <- first time upload
        else:
            date_query = f'SELECT MAX(crash_date) from {key}'
            with engine.connect() as connection:
                latest_db_date = connection.execute(text(date_query)).scalar() # <- subsequent uploads

            metadata = MetaData()
            metadata.reflect(bind=engine, only=[f'{key}'])
            current_date = latest_db_date
        #upsert data for past 30 days -> add new data

        looping_date = latest_api_date
        while looping_date>latest_db_date:
            df = get_data(mvc_data[key], key, latest_api_date)
            create_load_to_table(f'./{key}_metadata.yaml',engine,df,'collision_id')
            looping_date-=timedelta(days=1)
        
        
else:
    print("Please check connection")
        