
import requests as re

class api_extractor():
        def __init__(self, header, base_url, query, params):
              self.header = header
              self.base_url = base_url
              self.query = query
              self.params= params
              print ("check")
             

        def extract_first_time_load(self):
              session = re.Session()
              print (self.header)
              response = session.post(url = self.base_url, headers = self.header, json = self.query, params= self.params )
              print (response.status_code)
              data = response.json()
              return data
        
        def extract_incremental_load(self):
              session = re.Session()
              print (self.header)
              response = session.get(url = self.base_url, headers = self.header, json = self.query, params= self.params )
              print (response.status_code)
              data = response.json()
              return data
        







        





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





