import yaml
from pathlib import Path


def extract_config():

    config_file_parent_directory = Path(__file__).parent.parent.parent
    config_file_path = config_file_parent_directory/'config'
    with open (config_file_path/'config.yaml') as f:
        config = yaml.safe_load(f)
    return config




config = extract_config()
print (config)