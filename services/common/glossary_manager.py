"""
Custom Glossary Management System
Allows users to add, update, and manage domain-specific terms and definitions
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import asyncio
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class GlossaryManager:
    """Manages custom glossary terms for domains"""
    
    def __init__(self, domain_name: str, glossary_dir: Optional[str] = None):
        self.domain_name = domain_name.lower()
        self.glossary_dir = glossary_dir or self._get_default_glossary_dir()
        self.glossary_file = os.path.join(self.glossary_dir, f"{self.domain_name}_glossary.json")
        self._ensure_glossary_dir()
        self._load_glossary()
        self._lock = asyncio.Lock()
    
    def _get_default_glossary_dir(self) -> str:
        """Get default glossary directory"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'glossaries'
        )
    
    def _ensure_glossary_dir(self):
        """Ensure glossary directory exists"""
        Path(self.glossary_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_glossary(self):
        """Load glossary from file"""
        if os.path.exists(self.glossary_file):
            try:
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    self.glossary = json.load(f)
            except Exception as e:
                logger.error(f"Error loading glossary: {str(e)}")
                self.glossary = {}
        else:
            self.glossary = {}
    
    def _save_glossary(self):
        """Save glossary to file"""
        try:
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(self.glossary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving glossary: {str(e)}")
            raise
    
    async def add_term(self, term: str, definition: str, 
                      aliases: Optional[List[str]] = None,
                      category: Optional[str] = None,
                      examples: Optional[List[str]] = None,
                      related_terms: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new term to the glossary
        
        Args:
            term: The term to add
            definition: Definition of the term
            aliases: Alternative names for the term
            category: Category the term belongs to
            examples: Usage examples
            related_terms: Related terms in the glossary
            metadata: Additional metadata
            
        Returns:
            The created glossary entry
        """
        async with self._lock:
            term_key = term.lower().strip()
            
            if term_key in self.glossary:
                raise HTTPException(status_code=400, detail=f"Term '{term}' already exists")
            
            entry = {
                "term": term,
                "definition": definition,
                "aliases": aliases or [],
                "category": category or "general",
                "examples": examples or [],
                "related_terms": related_terms or [],
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": 1
            }
            
            self.glossary[term_key] = entry
            self._save_glossary()
            
            logger.info(f"Added term '{term}' to {self.domain_name} glossary")
            return entry
    
    async def update_term(self, term: str, 
                         definition: Optional[str] = None,
                         aliases: Optional[List[str]] = None,
                         category: Optional[str] = None,
                         examples: Optional[List[str]] = None,
                         related_terms: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update an existing term in the glossary"""
        async with self._lock:
            term_key = term.lower().strip()
            
            if term_key not in self.glossary:
                raise HTTPException(status_code=404, detail=f"Term '{term}' not found")
            
            entry = self.glossary[term_key]
            
            # Update fields if provided
            if definition is not None:
                entry["definition"] = definition
            if aliases is not None:
                entry["aliases"] = aliases
            if category is not None:
                entry["category"] = category
            if examples is not None:
                entry["examples"] = examples
            if related_terms is not None:
                entry["related_terms"] = related_terms
            if metadata is not None:
                entry["metadata"].update(metadata)
            
            entry["updated_at"] = datetime.utcnow().isoformat()
            entry["version"] = entry.get("version", 1) + 1
            
            self._save_glossary()
            
            logger.info(f"Updated term '{term}' in {self.domain_name} glossary")
            return entry
    
    async def delete_term(self, term: str) -> bool:
        """Delete a term from the glossary"""
        async with self._lock:
            term_key = term.lower().strip()
            
            if term_key not in self.glossary:
                raise HTTPException(status_code=404, detail=f"Term '{term}' not found")
            
            del self.glossary[term_key]
            self._save_glossary()
            
            logger.info(f"Deleted term '{term}' from {self.domain_name} glossary")
            return True
    
    async def get_term(self, term: str) -> Optional[Dict[str, Any]]:
        """Get a specific term from the glossary"""
        term_key = term.lower().strip()
        return self.glossary.get(term_key)
    
    async def search_terms(self, query: str, 
                          category: Optional[str] = None,
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for terms in the glossary
        
        Args:
            query: Search query
            category: Filter by category
            limit: Maximum number of results
            
        Returns:
            List of matching terms
        """
        query_lower = query.lower()
        results = []
        
        for term_key, entry in self.glossary.items():
            # Check if query matches term, definition, or aliases
            if (query_lower in term_key or 
                query_lower in entry["definition"].lower() or
                any(query_lower in alias.lower() for alias in entry.get("aliases", []))):
                
                # Apply category filter if specified
                if category and entry.get("category", "").lower() != category.lower():
                    continue
                
                results.append(entry)
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_all_terms(self, category: Optional[str] = None, 
                           page: int = 1, 
                           page_size: int = 50) -> Dict[str, Any]:
        """
        Get all terms with pagination
        
        Args:
            category: Filter by category
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Paginated results with metadata
        """
        # Filter by category if specified
        if category:
            filtered_terms = {
                k: v for k, v in self.glossary.items() 
                if v.get("category", "").lower() == category.lower()
            }
        else:
            filtered_terms = self.glossary
        
        # Calculate pagination
        total_items = len(filtered_terms)
        total_pages = (total_items + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page items
        items = list(filtered_terms.values())[start_idx:end_idx]
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories in the glossary"""
        categories = set()
        for entry in self.glossary.values():
            category = entry.get("category", "general")
            if category:
                categories.add(category)
        return sorted(list(categories))
    
    async def export_glossary(self, format: str = "json") -> Any:
        """
        Export glossary in different formats
        
        Args:
            format: Export format ('json', 'csv', 'markdown')
            
        Returns:
            Exported data in requested format
        """
        if format == "json":
            return self.glossary
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Term", "Definition", "Category", "Aliases", "Examples", "Related Terms"])
            
            # Write data
            for entry in self.glossary.values():
                writer.writerow([
                    entry["term"],
                    entry["definition"],
                    entry.get("category", "general"),
                    ", ".join(entry.get("aliases", [])),
                    " | ".join(entry.get("examples", [])),
                    ", ".join(entry.get("related_terms", []))
                ])
            
            return output.getvalue()
        
        elif format == "markdown":
            lines = [f"# {self.domain_name.upper()} Domain Glossary\n"]
            
            # Group by category
            categories = {}
            for entry in self.glossary.values():
                category = entry.get("category", "general")
                if category not in categories:
                    categories[category] = []
                categories[category].append(entry)
            
            # Write each category
            for category, entries in sorted(categories.items()):
                lines.append(f"\n## {category.title()}\n")
                
                for entry in sorted(entries, key=lambda x: x["term"]):
                    lines.append(f"### {entry['term']}\n")
                    lines.append(f"{entry['definition']}\n")
                    
                    if entry.get("aliases"):
                        lines.append(f"**Aliases:** {', '.join(entry['aliases'])}\n")
                    
                    if entry.get("examples"):
                        lines.append("\n**Examples:**")
                        for example in entry["examples"]:
                            lines.append(f"- {example}")
                        lines.append("")
                    
                    if entry.get("related_terms"):
                        lines.append(f"**Related Terms:** {', '.join(entry['related_terms'])}\n")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_glossary(self, data: Dict[str, Any], merge: bool = False):
        """
        Import glossary data
        
        Args:
            data: Glossary data to import
            merge: If True, merge with existing data; if False, replace
        """
        async with self._lock:
            if merge:
                # Merge with existing glossary
                for term_key, entry in data.items():
                    if term_key in self.glossary:
                        # Update version for existing terms
                        entry["version"] = self.glossary[term_key].get("version", 1) + 1
                        entry["updated_at"] = datetime.utcnow().isoformat()
                    else:
                        # New terms
                        entry["created_at"] = datetime.utcnow().isoformat()
                        entry["updated_at"] = datetime.utcnow().isoformat()
                        entry["version"] = 1
                    
                    self.glossary[term_key] = entry
            else:
                # Replace entire glossary
                self.glossary = data
            
            self._save_glossary()
            logger.info(f"Imported glossary data for {self.domain_name} domain")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get glossary statistics"""
        total_terms = len(self.glossary)
        categories = await self.get_categories()
        
        # Count terms per category
        category_counts = {}
        for entry in self.glossary.values():
            category = entry.get("category", "general")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Find most connected terms
        connection_counts = {}
        for entry in self.glossary.values():
            term = entry["term"]
            related = entry.get("related_terms", [])
            connection_counts[term] = len(related)
        
        most_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_terms": total_terms,
            "total_categories": len(categories),
            "terms_per_category": category_counts,
            "most_connected_terms": [{"term": term, "connections": count} for term, count in most_connected],
            "last_updated": max((entry["updated_at"] for entry in self.glossary.values()), default=None)
        }


def add_glossary_routes(app, domain_name: str):
    """Add glossary management routes to a FastAPI app"""
    from fastapi import Query
    from pydantic import BaseModel
    from typing import Optional, List
    
    glossary_manager = GlossaryManager(domain_name)
    
    class GlossaryTermCreate(BaseModel):
        term: str
        definition: str
        aliases: Optional[List[str]] = None
        category: Optional[str] = None
        examples: Optional[List[str]] = None
        related_terms: Optional[List[str]] = None
        metadata: Optional[Dict[str, Any]] = None
    
    class GlossaryTermUpdate(BaseModel):
        definition: Optional[str] = None
        aliases: Optional[List[str]] = None
        category: Optional[str] = None
        examples: Optional[List[str]] = None
        related_terms: Optional[List[str]] = None
        metadata: Optional[Dict[str, Any]] = None
    
    @app.post("/glossary/terms")
    async def create_glossary_term(term_data: GlossaryTermCreate):
        """Add a new term to the domain glossary"""
        return await glossary_manager.add_term(**term_data.dict())
    
    @app.get("/glossary/terms/{term}")
    async def get_glossary_term(term: str):
        """Get a specific term from the glossary"""
        result = await glossary_manager.get_term(term)
        if not result:
            raise HTTPException(status_code=404, detail=f"Term '{term}' not found")
        return result
    
    @app.put("/glossary/terms/{term}")
    async def update_glossary_term(term: str, update_data: GlossaryTermUpdate):
        """Update an existing term in the glossary"""
        return await glossary_manager.update_term(term, **update_data.dict(exclude_unset=True))
    
    @app.delete("/glossary/terms/{term}")
    async def delete_glossary_term(term: str):
        """Delete a term from the glossary"""
        await glossary_manager.delete_term(term)
        return {"message": f"Term '{term}' deleted successfully"}
    
    @app.get("/glossary/search")
    async def search_glossary(
        query: str = Query(..., description="Search query"),
        category: Optional[str] = Query(None, description="Filter by category"),
        limit: int = Query(10, ge=1, le=100, description="Maximum results")
    ):
        """Search for terms in the glossary"""
        return await glossary_manager.search_terms(query, category, limit)
    
    @app.get("/glossary/terms")
    async def list_glossary_terms(
        category: Optional[str] = Query(None, description="Filter by category"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=100, description="Items per page")
    ):
        """Get all glossary terms with pagination"""
        return await glossary_manager.get_all_terms(category, page, page_size)
    
    @app.get("/glossary/categories")
    async def get_glossary_categories():
        """Get all categories in the glossary"""
        return await glossary_manager.get_categories()
    
    @app.get("/glossary/export")
    async def export_glossary(
        format: str = Query("json", regex="^(json|csv|markdown)$", description="Export format")
    ):
        """Export glossary in different formats"""
        data = await glossary_manager.export_glossary(format)
        
        if format == "csv":
            from fastapi.responses import Response
            return Response(content=data, media_type="text/csv", 
                          headers={"Content-Disposition": f"attachment; filename={domain_name}_glossary.csv"})
        elif format == "markdown":
            from fastapi.responses import Response
            return Response(content=data, media_type="text/markdown",
                          headers={"Content-Disposition": f"attachment; filename={domain_name}_glossary.md"})
        else:
            return data
    
    @app.post("/glossary/import")
    async def import_glossary(data: Dict[str, Any], merge: bool = Query(False, description="Merge with existing data")):
        """Import glossary data"""
        await glossary_manager.import_glossary(data, merge)
        return {"message": "Glossary imported successfully"}
    
    @app.get("/glossary/stats")
    async def get_glossary_stats():
        """Get glossary statistics"""
        return await glossary_manager.get_stats()