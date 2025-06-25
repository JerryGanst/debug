"""
HR领域的具体配置
"""
import os
from dataclasses import dataclass
from typing import Dict
from domains.base import BaseDomainConfig


@dataclass
class DomainConfig(BaseDomainConfig):
    """HR领域配置类"""
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_NAME = "HR"
        self.DOMAIN_DOC_TYPE = "HR Infos" # 必须与DocumentType枚举类中的值匹配
        # 添加其他必要的自定义配置
        self.custom_config = {
            "topics": "人力资源政策、招聘流程、培训发展、绩效管理、薪酬福利",
            "systems": "智慧人资、OA、i学堂",
        }
    
    def get_prompt_template(self, template_name: str) -> str:
        """获取HR领域特定的提示词模板
        
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
            raise ValueError(f"HR领域的{template_name}模板不存在: {template_path}")
        except Exception as e:
            raise ValueError(f"无法读取HR领域的{template_name}模板: {str(e)}")
            
    def get_question_categories(self) -> Dict[int, str]:
        """获取HR领域特定的问题分类描述
        
        Returns:
            Dict[int, str]: 问题分类ID到描述的映射
        """
        return {
            1: "可以直接生成具体答案的问题（如考勤规定、工资计算方式、招聘流程、培训安排、绩效考核标准等具体事项）",
            2: "需要完整规章文件支持的问题（系统并返回相关文件，如员工手册、管理办法、劳动合同、考核制度、公司政策等）",
            3: "与公司管理无关的通用问题（如闲聊、一般职场建议、行业趋势、非企业内部的法律法规等）",
        } 