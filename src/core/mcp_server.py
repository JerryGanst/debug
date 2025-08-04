"""
FastMCP 2.0 Server with tag-based tool filtering.
"""

import logging
from typing import Dict, List, Set, Any, Optional
from fastmcp import FastMCP
from .tag_system import ToolTags, AgentProfile, get_agent_profile
from .config import ServerConfig
from .file_manager import FileManager

logger = logging.getLogger("excel-mcp")


class TaggedFastMCP:
    """
    FastMCP server wrapper with tag-based tool filtering.
    """
    
    def __init__(self, name: str, config: ServerConfig):
        self._mcp = FastMCP(name)
        self.config = config
        self.file_manager = FileManager(config)
        self._tool_tags: Dict[str, ToolTags] = {}
        self._current_agent_profile: Optional[AgentProfile] = None
    
    def set_agent_profile(self, agent_type: str = None, custom_tags: List[str] = None):
        """
        Set the current agent profile for tool filtering.
        
        Args:
            agent_type: Predefined agent type (e.g., 'excel_analyst')
            custom_tags: Custom tags for creating a custom agent profile
        """
        if agent_type:
            self._current_agent_profile = get_agent_profile(agent_type)
        elif custom_tags:
            from .tag_system import create_custom_agent
            self._current_agent_profile = create_custom_agent("custom", custom_tags)
        else:
            self._current_agent_profile = None
    
    def tool(self, **kwargs):
        """
        Decorator for registering tools with tags.
        
        Args:
            tags: ToolTags instance defining the tool's capabilities and permissions
            **kwargs: Additional arguments passed to FastMCP tool decorator
        """
        # Extract our custom tags parameter
        tags = kwargs.pop('tags', None)
        
        def decorator(func):
            # Register with FastMCP
            decorated_func = self._mcp.tool()(func)
            
            # Store tags for this tool
            if tags:
                self._tool_tags[func.__name__] = tags
            
            return decorated_func
        
        return decorator
    
    def run(self, **kwargs):
        """Run the underlying FastMCP server."""
        return self._mcp.run(**kwargs)
    
    def get_available_tools(self, agent_profile: AgentProfile = None) -> List[str]:
        """
        Get list of tools available to a specific agent profile.
        
        Args:
            agent_profile: Agent profile to check against, uses current if None
            
        Returns:
            List of tool names the agent can access
        """
        if agent_profile is None:
            agent_profile = self._current_agent_profile
        
        if agent_profile is None:
            # No filtering, return all tools
            return list(self._tool_tags.keys())
        
        available_tools = []
        for tool_name, tool_tags in self._tool_tags.items():
            if agent_profile.can_access_tool(tool_tags):
                available_tools.append(tool_name)
        
        return available_tools
    
    def filter_tools_for_agent(self, agent_type: str = None) -> Dict[str, Any]:
        """
        Filter and return tools available to a specific agent type.
        
        Args:
            agent_type: Type of agent to filter tools for
            
        Returns:
            Dictionary of available tools with their metadata
        """
        if agent_type:
            profile = get_agent_profile(agent_type)
        else:
            profile = self._current_agent_profile
        
        available_tools = self.get_available_tools(profile)
        
        # This would integrate with FastMCP's tool listing functionality
        return {
            "agent_type": agent_type or "current",
            "available_tools": available_tools,
            "total_tools": len(self._tool_tags),
            "filtered_tools": len(available_tools)
        }