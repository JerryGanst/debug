"""
基础领域配置类
所有具体领域配置都应该继承此类
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BaseDomainConfig:
    """基础领域配置类
    
    只包含最基本的领域标识信息，
    具体领域可以根据需要添加自己的特定配置
    """
    # 领域基本信息
    DOMAIN_NAME: str = "base"
    DOMAIN_DOC_TYPE: str = "BASE"
    
    # 领域可以自定义添加任何配置
    # 使用字典存储，而不是预定义固定字段
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_prompt_template(self, template_name: str) -> str:
        """获取指定名称的提示词模板
        
        子类应该重写此方法，返回领域特定的提示词模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            str: 提示词模板
        """
        raise NotImplementedError("子类必须实现get_prompt_template方法")
    
    def get_question_categories(self) -> Dict[int, str]:
        """获取领域特定的问题分类描述
        
        子类应该重写此方法，返回领域特定的问题分类描述
        
        Returns:
            Dict[int, str]: 问题分类ID到描述的映射
        """
        # 默认的问题分类
        return {
            1: "可以直接生成具体答案的问题",
            2: "需要完整规章文件支持的问题",
            3: "与领域无关的通用问题",
        } 