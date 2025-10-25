from jinja2 import Environment, FileSystemLoader
from config.config import *
from sqlalchemy import create_engine,text
from sqlalchemy.engine import Engine
import os

def extract(sql: str, engine: Engine) -> list[dict]:
    # return [dict(row) for row in engine.execute(sql).all()]
    with engine.connect() as conn:
        result = conn.execute(text(sql))
    
    return [row for row in result]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbconfig = DatabaseConfig()
engine = create_engine(dbconfig.create_url())

environment = Environment(loader = FileSystemLoader(os.path.join(BASE_DIR, 'sql')))
print(environment.list_templates())
for sql_path in environment.list_templates():
    sql_template = environment.get_template(sql_path)
    
    sql_query = sql_template.render()
    data = extract(sql_query, engine)
    print(data[0])
