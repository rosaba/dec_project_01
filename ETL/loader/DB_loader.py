
from auth.DB_auth import DB_auth
from sqlalchemy import MetaData, Table, Column, String, Integer, Date, DateTime, inspect, Float, BigInteger
from Utils.config_parser import extract_config

config_data =  extract_config()

class db_loader():
    def __init__(self, table_name, table_col):
        self.engine = DB_auth().create_engine()
        self.table_name = table_name
        self.table_col = table_col
     
        
    
    def create_metadata(self):

        # create a metada
        metadata = MetaData()
        

        type_map ={
            "Integer": Integer,
            "String" : String,
            "Date" : Date,
            "DateTime": DateTime,
            "Float": Float,
            "BigInteger": BigInteger
        }

        
        columns = []
        for col in self.table_col:
            col_type =  type_map[col["type"]]
            if col["type"] == "String" and "length" in col:
                col_type = String(col["length"])
                
            kwargs = {
                "primary_key": col.get("primary_key", False),
                "nullable": col.get("nullable", True),
                "unique": col.get("unique", False)
                }

            columns.append(Column(col["name"], col_type, **kwargs))
            
            # create table
        table = Table(self.table_name, metadata, *columns, extend_existing=True)
                

        # create a table
        metadata.create_all(self.engine)

        return table
            





        
        





