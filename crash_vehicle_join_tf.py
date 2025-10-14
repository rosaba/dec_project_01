import pandas as pd
from sodapy import Socrata 
from datetime import datetime, timedelta 
from sqlalchemy import create_engine 

# --- Configuration ---
DOMAIN = "data.cityofnewyork.us"
API_TOKEN = 'gczYtFY8Bn2j5CzBq2mMRu7la'
# DATASET = MV-Collisions - Crash 
DATASET = "h9gi-nx95"
# DATASET = MV-Collisions - Vehicles
VEHICLES_DATASET = "bm4k-52h4"


# Calculate date 730 days or 2 years from today
start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%dT00:00:00.000") 

# Calculate todays date
today = datetime.now().strftime("%Y-%m-%dT00:00:00.000")


# PostgreSQL connection details
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'nyc_collisions'
TABLE_NAME = 'crash'
VEHICLES_TABLE_NAME = "vehicles"

# --- Load crash Data ---
def fetch_data_range(start_date,end_date):

    client = Socrata(DOMAIN, API_TOKEN)

    results = client.get(DATASET) 
    
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

# --- Load vehicles Data ---
def fetch_vehicles_data_range(start_date, end_date):
    # timeout = 30 seconds to avoid running into timeout error 
    client = Socrata(DOMAIN, API_TOKEN, timeout = 30)
    
    results = []
    
    limit = 50000
    
    offset = 0
    # Fetch crash data from start_date >= 2 years ago from today AND end_date <= today
    while True:
        batch = client.get(VEHICLES_DATASET, where=f"crash_date >= '{start_date}' AND crash_date <= '{end_date}'", order="crash_date ASC", limit=limit, offset=offset)
        if not batch:
            break
        results.extend(batch)
        offset += limit

    return results

def fetch_vehicles_data():
    results = fetch_vehicles_data_range(start_date, today)
    return pd.DataFrame.from_records(results)


# --- category dictionary to clean vehicle_type_code1 data --- 
cat_dict = { "OTHERS" : ['1','12 PA','15 PA','2015','315 E','985', '99999', 'ACCES','ATTAC', 'BA', 'BACK', 'BACKH','BARRI','BOAT', 'BOBCA','BR', 'BS','BTM','BU', 'BULK AGRICULTURE',
 'c1','C1','C2','c3','C3','CABIN','CAMP','VAN CAMPER','Van Camper','CARRY ALL', 'CART','CATE','CB','CHERR','CITY','CUSHM', 'DEMA-','DP', 'DS', 'DOS TRUCK','DSNY', 'DUNBA', 'EAST', 'EN', 'ENCLOSED BODY - NONREMOVABLE ENCLOSURE', 
'ENCLOSED BODY - REMOVABLE ENCLOSURE', 'EPO', 'ESU T','FR', 'FRE', 'FREE','FRONT', 'FR`', 'FUEL', 'G COM', 'G SPC', 'G1`', 'GARBA','Garbage or Refuse', 'GARBAGE ST', 'garbage tr', 'Garbage tr', 'Garbage Tr', 'GARBAGE TR','Dumb Truck', 'DUMP', 'DUMPS', 'DUMPT','Dump', 'Dump truck', 'Dump Truck', 'DUMP TRUCK', 'DUMP TRUK',
'GARBAGE OR REFUSE', 'GATOR', 'GE/SC', 'GEICO', 'GG', 'GLASS RACK', 'GOKAR',
 'GR', 'GRAIN', 'GRAY', 'GRUMM', 'H/WH', 'HAND', 'HEAVY', 'HELP', 'HI TA','MOTER',
 'HO', 'HOPPER', 'HORSE', 'HRSE', 'HUMME', 'HWY C', 'ICE C', 'ICECR','KUBOT', 'L1', 'LADDE','LD', 'LF', 'LIBER', 'LIEBH', 'LIGHT', 'LIVESTOCK RACK', 'LL', 'LMB', 'LOADE', 'LOG', 'LP', 'LTR', 'LTRL', 
'LW', 'MARK', 'MARKE', 'MAXIM', 'MB', 'MC', 'MCY','MCY B', 'MD', 'ME/BE', 'MH', 'MILLI','MK', 'MO PA','MTR S', 
'MOBIL','MOTOR','MOTOR HOME','MOTORHOME', 'Motorized Home', 'Motor Home','MS','NAVIG', 'NEW Y', 'NISSA', 'NONE', 'NS AM', 'NTTRL', 'OLC', 'OML',
'OMR', 'OMT','OTHER', 'P/SE', 'P/SH', 'PALLET', 'PARCE',  'PAYLO', 'PC', 'PEDIC', 'PEDICAB','Pedicab','PL', 'PM','Postal Box',
'POWER', 'PRKS', 'PSD', 'PSH', 'PSR', 'PU', 'PUMP','R/V','rv','Quadricycl','R/V C','Rec Vehicl', 'RANGE', 'RD/S', 'RED T', 'REFG', 'REFRI', 'RENTA',
'REP', 'REPAI', 'RESCU', 'RF', 'RMB', 'RMP', 'RMP V', 'ROAD', 'RV', 'RV/TR','WINNIEBAGO','SANIT', 'SANTA', 'SANTI', 'SC','SCISS','SEAGR','SELF','SKATE', 'SKID-','SMART','SP', 
'SPC', 'SPC P', 'SPEC', 'SPRIN', 'SS', 'ST', 'STAK', 'STAKE OR RACK', 'STATE', 'SYBN', 'TCN', 'TE', 'TF', 'TIR', 'TK', 'TN', 'TRAFF','TRAIL','TRAM',
'TRC', 'TT',  'U.S.', 'VC', 'VERIZ', 'VN', 'VOL', 'VT',  'WD', 'WHBL','WHEEL', 'WHITE', 'WINEB', 'WINNE','UT','ULILI', 'UTIL', 'UTILI','utility', 'Utility', 'UTILITY', 'UTILITY TR', 'UTILITY VE','UTV','WAGON','wagon','VAGON','GOLF','golf cart', 'Golf cart', 'Golf Cart', 'GOLF CART', 'GOLFCART'],
"DEPT VEH" :['APORT', 'APPOR', 'AR','DEPT','PORTA','GOVER','NYC A', 'NYC B','NYC D', 'NYC F', 'NYC M', 'NYCHA', 'NYPD', 'NYS A','DOT R', 'DOT T','MTA', 'MTA B', 'MTA C', 'MTA T','Dept Tow t','DOT truck','Dot','NYPD TOW T','NYPD Traff'],
"EMERGENCY VEH" :['amb','Amb','ambu','Ambu','ambulance','Ambulance','AMBULANCE`','Ambulances','AMBULANE','AMBULENCE','Ambulette','AMBULETTE','Ï¿½MBU','AM', 'AMABU','AMB', 'AMBU', 'AMBUL', 'AMBULANCE','A', 'ABULA','E AMB',
                  'E.M.S','E - B','POLIC', 'EMRGN', 'EMS', 'EMS -BUS', 'EMS Ambule', 'EMS bus', 'EMS Bus', 'EMS FDNY', 'ems truck', 'EMS Truck','EMS A', 'EMS B', 'EMS H','ENGIN','Engine 26','FD FI', 'FD NY', 'FD TR', 'FDNY','FIRE TRUCK','FD Ambulan','FDNY 245 E','fdny ambul','FDNY ambul','FDNY Ambul','FDNY AMBUL','FDNY EMS','Fdny Ems T','FDNY EMS v','FDNY EMS V','FDNY EMS#1','FDNY ENGIN','Fdny fire','FDNY Fire','FDNY FIRE','fdny firet','FDNY FIRET',
                  'FIRETRUCK','FIRE','FDNY INSUR','FDNY Ladde','FDNY LADDE','FDNY truck','FDNY Truck','FDNY TRUCK','FDNY UTILI','FDNY VEHIC','FDNYTRUCKF','FIRE APPAR','Fire engin','Fire Engin','FIRE ENGIN','FIRE LADDE','fire truck','Fire truck','Fire Truck','firetruck','Firetruck','FIRETRUCK''FIRE', 'FIRET','NYC FIRE T','NYFD ambul','NYS AMBULA','Pvt Ambula','STREE','STREE SWE','Street swe','STREET SWE', 'SW', 'SWEEP','sweeper','SWEEPER TR','Rescue Tru','ROAD SWEEP','Road Sweep','DSNY SWEEP','LADDER', 'LADDER 169'],
"CONSTRUCTION VEH" :['Bearcat','Bobcat','BOBCAT','BOOM LIFT','Boom Lift','Bulldozer','BULLD','Cement tru','CEMENT TRU','CEMEN','CM', 'CMIX','COMIX','CONCR','Concrete Mixer', 'CONSTRUCTI','CAT 9', 'CAT P','(CEME','INTER','IP','BOOM','JOHN', 'KENWO','BUCKE',
           'CAT.','CONCRETE MIXER','EXCAV','DIRT','DIRTB','DOLLY','Excavator','LIFT', 'MAC T', 'MACK','LIFT BOOM','Mixer','CONST', 'CONT','FORK','fork lift','Fork lift','FORK LIFT','forklift','Forklift','FORKLIFT', 'FORK-', 'FORKL','Lift Boom','WELL DRILLER','WORK','SNOW PLOW','SNOW','CRANE'], 
"DELVERY VEH" :['Amazon del', 'AMAZON TRU', 'AMAZON VAN','courier', 'Courier', 'COURIER', 'COURIER VA','delivery', 'DELIVERY', 'Delivery t', 'Delivery T', 'DELIVERY T', 'Delivery V', 'DELIVERY V', 'DELIVRY TR','DEL', 'DELIV', 'DELV', 'DELVI', 'FOOD','Lunch Wagon','CMS-T','CATER','DOLLAR VAN','VAN','VAN (', 'VAN C','van', 'vAN', 'Van', 'Van (Trans', 'VAN BUS', 'VAN T', 'VAN/T', 'REFRIGERATED VAN','Refrigerated Van','VANG', 'VAV'],
"BICYCLE" :['BICYC', 'BICYCLE','Bicycle','BIKE','Bike', 'BK','Citi bike','MINICYCLE','Minicycle','PEDAL BIKE'],
"MOTORCYCLE" :['MOTORBIKE', 'MOTORCYCLE','MINIBIKE','Motorbike','Motorcycle','Minibike','Dirt Bike'],
"SEDAN": ['4 dr sedan', '4door', '4dsd','4WHEE','2 DR SEDAN','4 DR SEDAN','SEDAN','Sedan','SEDAN','4D','E450', '4DS', '4DSD','SE', 'SEA', '4WHEE','ST150','CONV', 'CONVE', 'CONVERTIBLE','Convertible', 'COUPE'],
"TRUCK" : ['AR', 'ARMOR', 'ARMORED TRUCK','Armored Truck','ARMY','U-HAU','UHAUL','UHUAL','U-Haul', 'U-HAUL', 'U-HAUL TRU', 'UHaul','BED T', 'BEVERAGE TRUCK','Beverage Truck','BOX', 'BOX T', 'BOX TRUCK','Box truck','Box Truck','Box Trucki',
           'BOXTR','truck', 'Truck', 'TRUCK', 'TRUCK CRAN', 'Truck/bus', 'TRUCK/VAN','TRUCK','TOW', 'TOW T', 'TOW TRUCK', 'TRK', 'TOW TRUCK / WRECKER','tow', 'Tow', 'TOW-TRUCK', 'tow truck', 'Tow truck', 'Tow Truck', 'Tow Truck / Wrecker', 'TOW-T', 'TOWTR','TR','Food Trail', 'food truck', 'FOOD TRUCK','Work truck','van truck','VAN TRUCK'],
"MAIL VEH" : ['COURI','FED E', 'MAIL','Mail truck','FEDER', 'FEDEX', 'FEDX','UPS T', 'US PO','USP M','USPOS', 'USPS','USPS2', 'POSTA','postal tru', 'POSTAL TRU', 'Postoffice','POSTO', 'POIS','UPS truck', 'UPS TRUCK', 'US MAIL #1', 'us postal', 'US Postal', 'US POSTAL', 'Usaa', 'USPS DELIV', 'USPS Mail', 'Usps truck', 'USPS Truck', 'USPS TRUCK', 'USPS VAN'],
"PASSENGER VEH" :['10 Paaseng','City Bus','charter bu','Panel Van', 'PSVAN','pas', 'Pass', 'Passanger', 'PASSANGER', 'Passenger', 'PASSENGER','PAS', 'PASS', 'PASSA', 'PASSE', 'PASSENGER VEHICLE','SCHOO', 'SCHOOL BUS','SCHOO LBUS','school bus','School bus','School Bus','School van','School Van','Small scho','sprinter','Sprinter','SPRINTER', 'sprinter v', 'Sprinter v', 'Sprinter V', 'SPRINTER V', 'BUS','bus','Bus','mini bus', 'COMMU','TRANS','OMNI', 'OMNIB','MOTORIZED HOME','NYC MTA BU','Mta bus', 'MTA bus', 'MTA Bus', 'MTA BUS', 'MTA BUS CO', 'NYC MTA BU', 'NYC School', 'NYC TRANSI','Yellow bus', 'Yellow sch', 'YELLOWBUS', 'YELLOWSCHO'],
"PICKUP" : ['CHEVO', 'CHEVY','CHASSIS CAB','Ford Pick','OPEN BODY','PICK','pick', 'PICK-UP', 'PICK-UP TR', 'Pick-up Truck', 'Pick up', 'PICK UP', 'Pick up tr', 'Pick up Tr', 'PICK UP TR', 'Pickup', 'Pickup tru', 'Pickup Tru', 'PICKUP TRU', 'Pickup with mounted Camper', 'PICK-', 'PICK-UP TRUCK', 'PICKU', 'LUNCH WAGON','PICKUP WITH MOUNTED CAMPER', 'PK', 'FORD','PKUP', 'F550', 'F650','RAM','VAB','VANETTE','Vanette'],
"SUV" :['CAR/SUV','SUB','4 RUN','SUBN','Honda HRV','SUBN/', 'SUBUR', 'SUV','subar', 'subn', 'Subn', 'SUBN/Van', 'Suburban', 'SUBURBAN', 'Surburban','White subu','JEEP','SW/SUV','SPORT UTILITY / STATION WAGON', 'Station Wa','STATION WAGON/SPORT UTILITY VEHICLE','Station Wagon/Sport Utility Vehicle','MINI', 'MINIV','Mini Van'],
"COMMERCIAL VEH": ['Chassis Cab','FLAT','BUDGE', 'FLAT BED','Flat Bed','Flat Rack','Flatbed','FLATBED','FLATBED TO','Flatbed Tr','CO', 'COM', 'COM T', 'COM.', 'COMB', 'COMER','COMM', 'COMM.', 'COMME','TANKE','FLAT RACK','CARGO','Cargo van','CARGO VAN',
           'FLAT/', 'FLATB','FREIG', 'FRHT', 'FRIEG','FREIGT VAN','FREIGHT', 'FREIGHT TR', 'freightlin','FB','HINO','Ice cream', 'Ice Cream','2 TON','35 FT','DIESE','MULTI-WHEELED VEHICLE','Mack truck', 'MACK TRUCK', 'Macktruck','SEMI','SEMI TRUCK','18 wheeler', 'SEMI-','MOVIN','OIL T',
           'TANKER','TANK','tank', 'TANK TRUCK', 'Tanker','TRACTOR TRUCK GASOLINE','RYDER','SMALL COM VEH(4 TIRES) ','LARGE COM VEH(6 OR MORE TIRES)','VERIZON TR',
           'COMMM','COMERCIAL', 'COMM TRAIL', 'commercial', 'Commercial', 'COMMERCIAL', 'commerical', 'COMMMERICA','sanitation', 'Sanitation', 'SANITATION','TRAC', 'TRAC.', 'TRACK', 'TRACT','TRACTOR TRUCK DIESEL','TRL', 'TRLPM', 'TRLR','Econoline','ECONOLINE','Track trai', 'Tractor', 'TRACTOR', 'TRACTOR CR', 'tractor tr', 'Tractor tr', 'Tractor Tr', 'TRACTOR TR', 'Tractor Truck Diesel', 'Tractor Truck Gasoline', 'trailer', 'Trailer', 'TRAILER', 'TRAILER CA', 'TRAILER VE', 'Tralier','WORK VAN'],
"TAXI" :['TAXI','taxi', 'Taxi', 'TAXI','YELLO','CAB','LIMO','Limousine','LIMOU', 'LIVER','LIVERY VEHICLE','Yellow Cab'],
"UNKOWN" :['UKN','UNK', 'UNKNO', 'UNKNOWN', 'UNKOW','Unk', 'Unknown', 'Unknown ve', 'Unkown'],
"SCOOTER" :['BLACK SCOO','Gas dirt b', 'Gas Moped', 'GAS MOPED', 'Gas Scoote', 'MO-PED', 'MOBILITY S', 'moped','Red moped', 'Moped', 'moped scoo', 'MOPPED', 'Motor scoo', 'MOTOR SCOO', 'MOTORSCOOT', 'Motorscooter','MOPAD', 'MOPD', 'MOPED','2 WHE','3 WHE','3-DOOR','Stand up s', 'Stand Up S', 'Standing s', 'Standing S','SCOO','3D', 'SCOOT','SCOOTER','MOTORSCOOTER','VESPA','scooter','Razor Scoo', 'RAZOR SCOO','Scooter','SCOOTER','SCOOTOR','seated sco'],
"ELECTRIC VEH" :['E BIK', 'E COM', 'E ONE', 'E SCO', 'E- BI', 'E-BIK','E-MOT', 'E-SCO','E/BIK','EBIKE', 'ELEC.','E-Bike', 'E-BIKE', 'e-scooter', 'E-scooter','Lime Scoot', 'E-Scooter', 'E bike', 'E scooter','Escooter', 'E SCOOTER', 'e1', 'Ebike', 'Electric B', 'Electric m', 'Electric M', 'ELECTRIC M', 'ELECTRIC S', 'ELECT','SGWS','SEGWA']}

# --- function that gets called later to clean/categorize vehicle_type_code1 data --- 
def getCategory(a):
    for i in cat_dict.keys(): #reaching the keys of dict
        # print(i)
        for x in cat_dict[i]:
            # print(x)
            a =a.replace(x,i)
    return a

# --- Transform Data ---
def transform_data(df, vehicles_df):

    # Convert to DataFrame & assign to a new df collisions
    collisions = pd.DataFrame.from_records(df)

    # Flatten 'location' column if it's a dict (json)
    if 'location' in collisions.columns:
        collisions['latitude'] = collisions['location'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
        collisions['longitude'] = collisions['location'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
        # extracing human_address from json  
        collisions['human_address'] = collisions['location'].apply(lambda x: x.get('human_address') if isinstance(x, dict) else None)
        # droping location field after extraction from json 
        collisions.drop(columns=['location'], inplace=True)
        # droping human_address after extraction from json 
        collisions.drop(columns=['human_address'], inplace=True) 

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

    # call getCategory function to clean/categorize the raw data in vehicle_type_code1 column and save it to new column vehicle_type_code1_clean 
    collisions["vehicle_type_code1_clean"] = getCategory(collisions["vehicle_type_code1"])

      # assign to a new DataFrame
    collisions_by_day = collisions   

    # convert all numeric columns to float64 and replace NaN values with 0.0
    numeric_columns = [
        'number_of_persons_injured',
        'number_of_persons_killed',
        'number_of_pedestrians_injured',
        'number_of_pedestrians_killed',
        'number_of_cyclist_injured',
        'number_of_cyclist_killed',
        'number_of_motorist_injured',
        'number_of_motorist_killed'
    ]

    for col in numeric_columns:
        collisions_by_day[col] = pd.to_numeric(collisions_by_day[col], errors='coerce').astype('float64').fillna(0.0)


    # Left join with vehicles dataset on collision_id 
    vehicles_subset = vehicles_df[['collision_id', 'pre_crash']]
    collisions_by_day = collisions_by_day.merge(vehicles_subset, on='collision_id', how='left')


    return collisions_by_day
    # print(collisions_by_day.head())
    # print(list(collisions_by_day.columns))
    # collisions_by_day.info()
    

# --- Save crash data to PostgreSQL ---
def save_to_postgres(collisions_by_day):
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(connection_string)
    collisions_by_day.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print(f"Data saved to PostgreSQL table: {TABLE_NAME} at {datetime.now()}")

# --- Save vehicles data to PostgreSQL ---
def save_vehicles_to_postgres(df):
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(connection_string)
    df.to_sql(VEHICLES_TABLE_NAME, engine, if_exists='replace', index=False)
    print(f"Data saved to PostgreSQL table: {VEHICLES_TABLE_NAME} at {datetime.now()}")

def main():
    # Crash data pipeline  
    collisions_by_day = fetch_data()

    # Vehicles data pipeline 
    vehicles_df = fetch_vehicles_data()    

    transformed_df = transform_data(collisions_by_day, vehicles_df)
    
    save_to_postgres(transformed_df)
    save_vehicles_to_postgres(vehicles_df)

if __name__ == "__main__":
    main()
