import yaml
import os
from types import SimpleNamespace

def load_configs():
    # Load configurations from configs.yaml
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs.yaml')
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Merge MCP_CONFIG and MINIO_CONFIG
    merged_config = {}
    if 'MCP_CONFIG' in config_data:
        merged_config.update(config_data['MCP_CONFIG'])
    if 'MINIO_CONFIG' in config_data:
        merged_config.update(config_data['MINIO_CONFIG'])
    
    # Return as SimpleNamespace for dot notation access
    return SimpleNamespace(**merged_config)