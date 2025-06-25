"""
IT领域的具体配置
"""
import os
from dataclasses import dataclass
from typing import Dict
from domains.base import BaseDomainConfig


@dataclass
class DomainConfig(BaseDomainConfig):
    """IT领域配置类"""
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_NAME = "IT"
        self.DOMAIN_DOC_TYPE = "IT"
        # 添加其他必要的自定义配置
        self.custom_config = {
            "topics": "技术支持、系统开发、IT 政策、数据安全、网络管理",
            "systems": "LDP（立讯数字化平台）、MES、SAP、OA、Luxlink、2025",
        }
    
    def get_prompt_template(self, template_name: str) -> str:
        """获取IT领域特定的提示词模板
        
        Args:
            template_name: 模板名称，如 'question_classification', 'answer_generation' 等
            
        Returns:
            str: 提示词模板内容
        """
        # 构建模板文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, 'templates', f'{template_name}.txt')
        
        # 读取模板文件
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"IT领域的{template_name}模板不存在: {template_path}")
        except Exception as e:
            raise ValueError(f"无法读取IT领域的{template_name}模板: {str(e)}")
            
    def get_question_categories(self) -> Dict[int, str]:
        """获取IT领域特定的问题分类描述
        
        Returns:
            Dict[int, str]: 问题分类ID到描述的映射
        """
        return {
            1: "可以直接生成具体答案的问题（如技术支持流程、系统部署步骤、IT 设备申请规则、权限管理规范、数据备份频率等具体事项）",
            2: "需要完整规章文件支持的问题（系统并返回相关文件，如 IT 服务管理政策、数据安全规范、网络使用手册、开发流程文档、IT 合规政策等）",
            3: "与 IT 管理无关的通用问题（如闲聊、一般职业建议、行业趋势、非企业内部的技术问题等）",
        } 