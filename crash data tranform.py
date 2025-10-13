import pandas as pd
from sodapy import Socrata 
from datetime import datetime, timedelta 
from sqlalchemy import create_engine 

# --- Configuration ---
DOMAIN = "data.cityofnewyork.us"
API_TOKEN = 'gczYtFY8Bn2j5CzBq2mMRu7la'
# DATASET = MV-Collisions - Crash 
DATASET = "h9gi-nx95"

# Calculate date 730 days or 2 years from today
start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%dT00:00:00.000") 

# Calculate date 6 months ago from today
# six_mos_ago = (datetime.now() - timedelta(days=182.5)).strftime("%Y-%m-%dT00:00:00.000")

# Calculate date 6 months ago from today
# six_mos_ago_2 = six_mos_ago

# Calculate todays date
today = datetime.now().strftime("%Y-%m-%dT00:00:00.000")


# PostgreSQL connection details
DB_USER = 'postgres'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'nyc_collisions'
TABLE_NAME = 'crash'


# --- Load Data ---
def fetch_data_range(start_date,end_date):

    client = Socrata(DOMAIN, API_TOKEN)

    results = client.get(DATASET) 
                        
    # Fetch crash data from the last 30 days
    # results = client.get(DATASET,where=f"crash_date >= '{thirty_days_ago}'", limit = 50000)
    
    results = []

    limit = 50000

    offset = 0 
    # Fetch crash data from start_date >= 2 years ago from today AND end_date <= today
    while True: 
            batch = client.get(DATASET,where=f"crash_date >= '{start_date}' AND crash_date <= '{end_date}'", order="crash_date ASC", limit=limit, offset=offset)
            if not batch: 
                 break
            results.extend(batch)
            offset += limit 

    return results

def fetch_data():
     results = fetch_data_range(start_date, today)

     all_results = results 

     return pd.DataFrame.from_records(all_results)

# --- Transform Data ---
def transform_data(df):

    # Convert to DataFrame & assign to a new df collisions
    collisions = pd.DataFrame.from_records(df)

    # Flatten 'location' column if it's a dict 
    if 'location' in collisions.columns:
        collisions['latitude'] = collisions['location'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
        collisions['longitude'] = collisions['location'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
        collisions['human_address'] = collisions['location'].apply(lambda x: x.get('human_address') if isinstance(x, dict) else None)
        collisions.drop(columns=['location'], inplace=True) 

    # converts the crash_date column from string format to datetime in Pandas.
    collisions['crash_date'] = pd.to_datetime(collisions['crash_date'],infer_datetime_format=True)
    # converts the crash_time column from string format to AM/PM time in Pandas.
    collisions['crash_time'] = pd.to_datetime(collisions['crash_time'],format='%H:%M').dt.strftime('%I:%M %p') 

    # replaces any missing or null values in the BOROUGH column with NYC
    collisions["borough"] = collisions["borough"].fillna("NYC")

    # adds a new column called day_of_week to the collisions DataFrame, which contains the name of the weekday (e.g., "Monday", "Tuesday") for each crash date.
    collisions['day_of_week'] = collisions['crash_date'].dt.day_name()

    # adds a new column called Weekend_Weekday
    collisions['Weekend_Weekday'] = collisions['day_of_week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday') 

    # assign to a new DataFrame
    collisions_by_day = collisions 
    return collisions_by_day
    # print(collisions_by_day.head())
    # print(list(collisions_by_day.columns))
    # collisions_by_day.info()

# --- Save to PostgreSQL ---
def save_to_postgres(collisions_by_day):
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(connection_string)
    collisions_by_day.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print(f"Data saved to PostgreSQL table: {TABLE_NAME} at {datetime.now()}")

def main():
    collisions_by_day = fetch_data()
    transformed_df = transform_data(collisions_by_day)
    save_to_postgres(transformed_df)

if __name__ == "__main__":
    main()

