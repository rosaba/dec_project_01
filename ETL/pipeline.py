
from pathlib import Path
from auth.API_auth import api_Authentication
from extractor.api_extractor import api_extractor
from Utils import config_parser
import pandas as pd
from pathlib import Path


config_data =  config_parser.extract_config()

class pipeline():
    def __init__(self, config:dict):
        self.config = config
        

    def extract_data_crashes(self):   
         # authenticate
        extract_path = Path(__file__).parent.parent/'crashes.csv'
        auth = api_Authentication()   
        header =  auth.headers()
        if not extract_path.exists():
            extract_object  = api_extractor(header,self.config['base_url']['crashes'],  self.config['first_time_load'],  params = 'None')
            first_load = extract_object.extract_first_time_load()
            df_crashes = pd.json_normalize(first_load)
            df_crashes.to_csv("crashes.csv")
            return df_crashes
            
        else:
               # max_date = df["crash_date"].max()
            extract_object  = api_extractor(header, self.config['base_url']['crashes'],  self.config['max_date_data'],   params = 'None')
            max_date_crash_json = extract_object.extract_first_time_load()
            max_date_data = max_date_crash_json[0]['max_crash_date']
            params_query = config_data["params_query"]
            params_query["$where"] = params_query["$where"].format(max_date=max_date_data)
            extract_object  = api_extractor(header, self.config['base_url']['crashes'], query = 'None' , params = params_query)
            incremental_data = extract_object.extract_incremental_load()
            incremental_data = pd.json_normalize(incremental_data)
            incremental_data.to_csv("crashes.csv", mode= 'a')
            df_crashes = pd.read_csv("crashes.csv")
            updated_data_crashes = pd.concat([incremental_data, df_crashes], ignore_index= True)
            return updated_data_crashes
      


    def extract_data_vehicles(self):   
         # authenticate
        extract_path = Path(__file__).parent.parent/'vehicles.csv'
        auth = api_Authentication()   
        header =  auth.headers()
        if not extract_path.exists():
            extract_object  = api_extractor(header,self.config['base_url']['vehicles'],  self.config['first_time_load'],  params = 'None')
            first_load = extract_object.extract_first_time_load()
            df_vehicles = pd.json_normalize(first_load)
            df_vehicles.to_csv("vehicles.csv")
            return df_vehicles
            
        else:
               # max_date = df["crash_date"].max()
            extract_object  = api_extractor(header, self.config['base_url']['vehicles'],  self.config['max_date_data'],   params = 'None')
            max_date_crash_json = extract_object.extract_first_time_load()
            max_date_data = max_date_crash_json[0]['max_crash_date']
            params_query = config_data["params_query"]
            params_query["$where"] = params_query["$where"].format(max_date=max_date_data)
            extract_object  = api_extractor(header, self.config['base_url']['vehicles'], query = 'None' , params = params_query)
            incremental_data = extract_object.extract_incremental_load()
            incremental_data = pd.json_normalize(incremental_data)
            incremental_data.to_csv("vehicles.csv", mode= 'a')
            updated_data_vehicles = pd.concat([incremental_data, df_vehicles], ignore_index= True)
            return updated_data_vehicles
            


    def extract_data_person(self):   
         # authenticate
        extract_path = Path(__file__).parent.parent/'person.csv'
        auth = api_Authentication()   
        header =  auth.headers()
        if not extract_path.exists():
            extract_object  = api_extractor(header,self.config['base_url']['person'],  self.config['first_time_load'],  params = 'None')
            first_load = extract_object.extract_first_time_load()
            df_person = pd.json_normalize(first_load)
            df_person.to_csv("person.csv")
            return df_person

        else:
               # max_date = df["crash_date"].max()
            extract_object  = api_extractor(header, self.config['base_url']['person'],  self.config['max_date_data'],   params = 'None')
            max_date_crash_json = extract_object.extract_first_time_load()
            max_date_data = max_date_crash_json[0]['max_crash_date']
            params_query = config_data["params_query"]
            params_query["$where"] = params_query["$where"].format(max_date=max_date_data)
            extract_object  = api_extractor(header, self.config['base_url']['person'], query = 'None' , params = params_query)
            incremental_data = extract_object.extract_incremental_load()
            incremental_data = pd.json_normalize(incremental_data)
            incremental_data.to_csv("person.csv", mode= 'a')  
            updated_data_person = pd.concat([incremental_data, df_person], ignore_index= True)
            return updated_data_person
        


                  

p = pipeline(config= config_data)
p.extract_data_crashes()
p.extract_data_person()
p.extract_data_vehicles()