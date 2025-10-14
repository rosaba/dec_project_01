import tempfile
import pandas as pd
from sqlalchemy import create_engine, text
from load.load import create_load_to_table

def test_create_load_to_table_appends():
    
    yaml_content = "primary_key: id\ntest_table:\n  - id: Integer\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        yaml_file = f.name
    
    engine = create_engine('sqlite:///:memory:')
    
    # Load twice
    df1 = pd.DataFrame({'id': [1]})
    create_load_to_table(yaml_file, engine, df1)
    
    df2 = pd.DataFrame({'id': [2]})
    create_load_to_table(yaml_file, engine, df2)
    
    # Should have 2 rows
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM test_table")).scalar()
        assert count == 2