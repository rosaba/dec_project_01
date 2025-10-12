
import requests as re
import pandas as pd
from auth.API_auth import api_Authentication



class api_extractor():
        def __init__(self, base_url, params,  query,):
              auth = api_Authentication()
              self.header = auth.headers()
              self.base_url = base_url
              self.query = query
              self.params= params
            
             

        def extract(self):
              session = re.Session()
              response = session.get(url = self.base_url, headers = self.header, params= self.params )
              json_data = response.json()
              data = pd.json_normalize(json_data)
              return data
             
              
           
             
             
        
        
        # def extract_incremental_load(self):
        #       session = re.Session()
        #       response = session.get(url = self.base_url, headers = self.header, json = self.query, params= self.params )
        #       incremental_load = response.json()
        #       df_incremental_load = pd.json_normalize(incremental_load)
        #       return df_incremental_load
        

        







        





# extract max date 
# extract max of crash date in df
# compare if equal do nothting if not then extract data and upsert




# data = {
#     "query" : f"Select * having max(crash_date) < {current_date} "
# }

# data = {
#     "where": f"crash_date < '{current_date}'",
#     "limit": 1000
# }

    
# print (data["query"])

# response = re.post(url= crash_url , headers= header, json= data)
# print (response.status_code)
# df = pd.json_normalize(response.json())
# print (df.head(10))





