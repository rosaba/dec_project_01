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
    for key in mvc_data.keys():
        latest_date = get_date(mvc_data[key],'SELECT * ORDER BY crash_date DESC LIMIT 1')
        earliest_date = latest_date - timedelta(days=3) #setting up 'border-date', test to see upload of 3 days
        while latest_date>earliest_date:
            df = get_data(mvc_data[key], key, latest_date)
            create_load_to_table(f'./{key}_metadata.yaml',engine,df)
            latest_date-=timedelta(days=1)
else:
    print("Please check connection")
        