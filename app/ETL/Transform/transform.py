import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:

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