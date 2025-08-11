"""
File management utilities with concurrent access protection.
"""

from pathlib import Path
from typing import Union
from contextlib import contextmanager
import filelock
from .config import ServerConfig


class FileManager:
    """
    Manages file operations with locking for concurrent access protection.
    """
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self._ensure_base_directory()
    
    def _ensure_base_directory(self):
        """Ensure the base excel files directory exists."""
        base_path = Path(self.config.mcp.excel_files_path)
        base_path.mkdir(parents=True, exist_ok=True)
    
    def get_user_directory(self, user_id: str) -> Path:
        """
        Get the directory path for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Path object for user directory
        """
        user_dir = Path(self.config.mcp.excel_files_path) / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def get_file_path(self, filename: str, user_id: str) -> Path:
        """
        Get the full path for a user's file.
        
        Args:
            filename: Name of the file (without path)
            user_id: User identifier
            
        Returns:
            Full path to the file
        """
        # Extract just the filename from any path input to avoid confusion
        filename = Path(filename).name
        return self.get_user_directory(user_id) / filename
    
    @contextmanager
    def lock_file(self, file_path: Union[str, Path], timeout: float = 30.0):
        """
        Context manager for file locking.
        
        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock (seconds)
            
        Raises:
            TimeoutError: If lock cannot be acquired within timeout
        """
        lock_path = Path(str(file_path) + '.lock')
        lock = filelock.FileLock(lock_path, timeout=timeout)
        lock_acquired = False

        try:
            lock.acquire()
            lock_acquired = True
            yield file_path
        finally:
            if lock_acquired:
                lock.release()


def get_safe_filename(filename: str) -> str:
    """
    Extract safe filename from path and ensure it's just a filename.
    
    Args:
        filename: Input filename or path
        
    Returns:
        Safe filename without path components
    """
    return Path(filename).name