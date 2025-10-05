
from dotenv import load_dotenv
import os


class api_Authentication:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('API_TOKEN')
       
    

    def headers(self):
        if not self.API_KEY :
            raise ValueError(" Missing API key! Check your .env file.")
        else:
            header = {
                        "X-App-Token": self.API_KEY,   # depends on API type
                        "Content-Type": "application/json" }
        return header