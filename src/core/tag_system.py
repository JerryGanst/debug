"""
Tag-based tool filtering system for MCP agents.
"""

from typing import Set, List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class FunctionalDomain(Enum):
    """Functional domain categories for tools."""
    EXCEL = "excel"
    MINIO = "minio"
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    TRANSLATION = "translation"
    GENERAL = "general"


class PermissionLevel(Enum):
    """Permission levels for tools."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class ResourceType(Enum):
    """Resource types that tools operate on."""
    FILE = "file"
    DATA = "data"
    CHART = "chart"
    PIVOT = "pivot"
    FORMAT = "format"
    VALIDATION = "validation"
    WORKBOOK = "workbook"
    SHEET = "sheet"
    CELL = "cell"
    STORAGE = "storage"


class Scope(Enum):
    """Scope of tool operation."""
    USER_SCOPED = "user_scoped"
    GLOBAL = "global"
    SHARED = "shared"


@dataclass
class ToolTags:
    """Container for tool tags across multiple dimensions."""
    functional_domains: Set[FunctionalDomain]
    permissions: Set[PermissionLevel]
    resource_types: Set[ResourceType]
    scopes: Set[Scope]
    
    def __init__(self, 
                 functional_domains: List[str] = None,
                 permissions: List[str] = None,
                 resource_types: List[str] = None,
                 scopes: List[str] = None):
        self.functional_domains = {FunctionalDomain(d) for d in (functional_domains or [])}
        self.permissions = {PermissionLevel(p) for p in (permissions or [])}
        self.resource_types = {ResourceType(r) for r in (resource_types or [])}
        self.scopes = {Scope(s) for s in (scopes or [])}
    
    def to_string_set(self) -> Set[str]:
        """Convert all tags to a flat string set for easy comparison."""
        tags = set()
        tags.update(d.value for d in self.functional_domains)
        tags.update(p.value for p in self.permissions)
        tags.update(r.value for r in self.resource_types)
        tags.update(s.value for s in self.scopes)
        return tags
    
    def matches_requirements(self, required_tags: Set[str]) -> bool:
        """Check if this tool's tags match agent requirements."""
        tool_tags = self.to_string_set()
        
        # Must have at least one matching tag, but if agent specifies
        # domain + permission, tool must have both
        intersection = required_tags.intersection(tool_tags)
        
        if len(intersection) == 0:
            return False
            
        # For multi-tag requirements, check domain matching more carefully
        if len(required_tags) > 1:
            # If agent wants specific domain (minio/excel), tool must have that domain
            for domain in ['minio', 'excel']:
                if domain in required_tags and domain not in tool_tags:
                    return False
        
        return True


class AgentProfile:
    """Defines what tools an agent can access based on tags."""
    
    def __init__(self, name: str, required_tags: Set[str]):
        self.name = name
        self.required_tags = required_tags
    
    def can_access_tool(self, tool_tags: ToolTags) -> bool:
        """Check if this agent can access a tool with given tags."""
        # Admin can access all tools
        if "admin" in self.required_tags:
            return True
        return tool_tags.matches_requirements(self.required_tags)


# Predefined agent profiles for common use cases
AGENT_PROFILES = {
    "excel_analyst": AgentProfile(
        name="Excel Analysis Agent",
        required_tags={"read"}  # Only read operations
    ),
    "excel_editor": AgentProfile(
        name="Excel Editor Agent", 
        required_tags={"excel", "write", "user_scoped"}
    ),
    "minio_reader": AgentProfile(
        name="MinIO Read-only Agent",
        required_tags={"minio", "read"}  # MinIO read operations only
    ),
    "minio_manager": AgentProfile(
        name="MinIO Management Agent",
        required_tags={"minio", "write", "storage", "user_scoped"}
    ),
    "data_scientist": AgentProfile(
        name="Data Science Agent",
        required_tags={"excel", "data", "chart", "pivot"}  # Advanced data analysis
    ),
    "report_generator": AgentProfile(
        name="Report Generator Agent", 
        required_tags={"excel", "format", "chart"}  # Formatting and charts
    ),
    "admin": AgentProfile(
        name="Administrator Agent",
        required_tags={"admin"}  # Admin can access everything
    )
}


def get_agent_profile(agent_type: str) -> Optional[AgentProfile]:
    """Get predefined agent profile by type."""
    return AGENT_PROFILES.get(agent_type)


def create_custom_agent(name: str, required_tags: List[str]) -> AgentProfile:
    """Create a custom agent profile with specific tag requirements."""
    return AgentProfile(name, set(required_tags))