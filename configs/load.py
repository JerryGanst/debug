# Load configuration from external YAML file
import yaml


def load_config(section=None):
    with open("configs/agent_configs.yaml", "r", encoding="utf-8") as file:
        total_config = yaml.safe_load(file)

    if not section:
        return total_config

    return total_config.get(section, {})

class ModelRouter:
    def __init__(self, config):
        self.models = config['models']
        self.modules = config['modules']
        # Safely access 'context_retrieval' and 'embedding_batch_endpoint', handle missing keys gracefully
        self.embedding_batch_api_url = (
            config.get('context_retrieval', {}).get('embedding_batch_endpoint')
        )

    # 获取用户指定模型或者模块默认模型的配置
    def get_model_config(self, module_name, user_selected_model=None):
        model_name = user_selected_model or self.modules[module_name]['default_model']
        return self.models[model_name]
    # 获取指定模块配置
    def get_module_config(self,module_name):
        return self.modules[module_name]
    # 获取embedding batch服务的api_url
    def get_embedding_batch_api_url(self):
        return self.embedding_batch_api_url