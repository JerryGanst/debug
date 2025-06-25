"""
领域注册表
用于自动发现和加载系统中可用的领域配置
"""
import importlib
import os
import pkgutil
import logging

from domains.base import BaseDomainConfig

logger = logging.getLogger(__name__)
_domain_registry = {}


def discover_domains():
    """自动发现所有可用的领域模块
    
    扫描domains目录下的子目录，查找并加载每个领域的配置类
    """
    import domains
    domains_path = os.path.dirname(domains.__file__)
    
    for _, name, is_pkg in pkgutil.iter_modules([domains_path]):
        if is_pkg and name not in ['__pycache__']:
            try:
                # 尝试从领域包中导入config模块
                module = importlib.import_module(f'domains.{name}.config')
                if hasattr(module, 'DomainConfig'):
                    config_class = module.DomainConfig
                    # 实例化配置并注册到领域注册表中
                    config_instance = config_class()
                    domain_name = name.lower()
                    _domain_registry[domain_name] = config_instance
                    logger.info(f"已注册领域: {domain_name}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"无法加载领域 {name}: {str(e)}")


def get_domain_config(domain_name=None):
    """获取指定领域配置
    
    Args:
        domain_name: 领域名称，如果为None则使用环境变量或默认值
        
    Returns:
        BaseDomainConfig: 领域配置对象
    """
    if not _domain_registry:
        discover_domains()
    
    if domain_name is None:
        domain_name = os.environ.get('DOMAIN_NAME', 'it')
        
    domain_name = domain_name.lower()
    if domain_name in _domain_registry:
        return _domain_registry[domain_name]
    
    # 找不到指定领域则返回默认配置（IT领域）
    default_domain = 'it'
    if default_domain in _domain_registry:
        logger.warning(f"未找到领域 '{domain_name}'，使用默认领域 '{default_domain}'")
        return _domain_registry[default_domain]
    
    # 如果连默认领域也没有，返回基础配置
    logger.warning(f"未找到默认领域 '{default_domain}'，使用基础配置")
    return BaseDomainConfig()


# 初始化时自动发现可用领域
discover_domains() 