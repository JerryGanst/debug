"""
领域上下文管理类
采用单例模式，保证整个应用程序中只有一个活动的领域配置
"""
import os
import logging
from configs.load_env import settings

logger = logging.getLogger(__name__)

class DomainContext:
    """领域上下文管理类，采用单例模式"""
    _instance = None
    _domain_config = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainContext, cls).__new__(cls)
            cls._instance._domain_config = None
            cls._instance._initialized = False
        return cls._instance
    
    @classmethod
    def initialize(cls, domain_name=None):
        """应用启动时初始化领域配置
        
        Args:
            domain_name: 领域名称，如果为None则使用环境变量或默认值
            
        Returns:
            DomainContext: 上下文单例实例
        """
        instance = cls()
        
        # 如果已经初始化且没有指定新的领域名称，直接返回
        if instance._initialized and domain_name is None:
            logger.info("DomainContext已初始化，使用现有配置")
            return instance
            
        # 如果已经初始化，但指定了新的领域名称，记录重新初始化信息
        if instance._initialized:
            logger.warning(f"DomainContext已初始化，但正在切换到新领域: {domain_name}")
        
        from domains.registry import get_domain_config
        instance._domain_config = get_domain_config(domain_name)
        instance._initialized = True
        
        logger.info(f"已初始化领域: {instance._domain_config.DOMAIN_NAME}")
        return instance
    
    @classmethod
    def get_config(cls):
        """获取当前活动的领域配置
        
        如果未初始化，则使用环境变量或.env文件中指定的领域进行懒加载
        
        Returns:
            BaseDomainConfig: 当前活动的领域配置对象
        """
        instance = cls()
        if not instance._initialized or instance._domain_config is None:
            logger.info("DomainContext尚未初始化，使用环境变量或.env文件进行懒加载")
            domain_name = os.environ.get('DOMAIN_NAME') or settings.domain_name
            return cls.initialize(domain_name)._domain_config
        return instance._domain_config
        
    @classmethod
    def is_initialized(cls):
        """检查是否已初始化
        
        Returns:
            bool: 是否已初始化
        """
        return cls._instance is not None and cls._instance._initialized 