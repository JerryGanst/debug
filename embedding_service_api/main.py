#!/usr/bin/env python3
"""
Standalone Embedding Service
Provides text embedding functionality as a separate microservice
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
import logging
import os
import sys
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import embedding functionality from existing service
from embedding_service import EmbeddingClient, EmbeddingCache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thread pool for CPU-bound operations
thread_pool = ThreadPoolExecutor(max_workers=4)

# Initialize FastAPI app
app = FastAPI(
    title="Embedding Service API",
    version="1.0.0",
    description="Standalone service for generating text embeddings"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize embedding client
embedding_client = EmbeddingClient()
embedding_cache = EmbeddingCache()


# Request/Response models
class EmbeddingRequest(BaseModel):
    text: Union[str, List[str]]
    model: Optional[str] = "text-embedding-ada-002"
    use_cache: bool = True


class EmbeddingResponse(BaseModel):
    embeddings: Union[List[float], List[List[float]]]
    model: str
    usage: dict
    cached: bool = False


class SimilarityRequest(BaseModel):
    text1: str
    text2: str
    model: Optional[str] = "text-embedding-ada-002"


class SimilarityResponse(BaseModel):
    similarity: float
    model: str


class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = "text-embedding-ada-002"
    batch_size: int = 50
    use_cache: bool = True


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Embedding Service",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_enabled": embedding_cache.enabled
    }


@app.post("/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for text or list of texts
    """
    try:
        # Check if single text or list
        is_single = isinstance(request.text, str)
        texts = [request.text] if is_single else request.text
        
        embeddings = []
        cached = False
        total_tokens = 0
        
        # Process each text
        for text in texts:
            # Check cache if enabled
            if request.use_cache:
                cached_embedding = await embedding_cache.get(text, request.model)
                if cached_embedding is not None:
                    embeddings.append(cached_embedding)
                    cached = True
                    continue
            
            # Generate embedding
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                thread_pool, 
                embedding_client.get_embedding,
                text,
                request.model
            )
            
            embeddings.append(embedding)
            
            # Cache the result
            if request.use_cache:
                await embedding_cache.set(text, request.model, embedding)
            
            # Estimate token usage (rough approximation)
            total_tokens += len(text.split()) * 1.3
        
        # Return single embedding or list
        final_embeddings = embeddings[0] if is_single else embeddings
        
        return EmbeddingResponse(
            embeddings=final_embeddings,
            model=request.model,
            usage={
                "prompt_tokens": int(total_tokens),
                "total_tokens": int(total_tokens)
            },
            cached=cached
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embeddings/batch", response_model=EmbeddingResponse)
async def get_batch_embeddings(request: BatchEmbeddingRequest):
    """
    Generate embeddings for a batch of texts with optimized processing
    """
    try:
        embeddings = []
        total_tokens = 0
        cached_count = 0
        
        # Process in batches
        for i in range(0, len(request.texts), request.batch_size):
            batch_texts = request.texts[i:i + request.batch_size]
            batch_embeddings = []
            
            # Check cache for each text in batch
            texts_to_embed = []
            cache_indices = []
            
            for idx, text in enumerate(batch_texts):
                if request.use_cache:
                    cached_embedding = await embedding_cache.get(text, request.model)
                    if cached_embedding is not None:
                        batch_embeddings.append((idx, cached_embedding))
                        cached_count += 1
                        continue
                
                texts_to_embed.append(text)
                cache_indices.append(idx)
            
            # Generate embeddings for non-cached texts
            if texts_to_embed:
                # Process in parallel
                tasks = []
                for text in texts_to_embed:
                    task = asyncio.create_task(
                        asyncio.to_thread(
                            embedding_client.get_embedding,
                            text,
                            request.model
                        )
                    )
                    tasks.append(task)
                
                new_embeddings = await asyncio.gather(*tasks)
                
                # Cache new embeddings
                if request.use_cache:
                    cache_tasks = []
                    for text, embedding in zip(texts_to_embed, new_embeddings):
                        cache_task = embedding_cache.set(text, request.model, embedding)
                        cache_tasks.append(cache_task)
                    await asyncio.gather(*cache_tasks)
                
                # Combine with cached embeddings
                for idx, embedding in zip(cache_indices, new_embeddings):
                    batch_embeddings.append((idx, embedding))
            
            # Sort by original index and extract embeddings
            batch_embeddings.sort(key=lambda x: x[0])
            embeddings.extend([emb for _, emb in batch_embeddings])
            
            # Estimate tokens
            total_tokens += sum(len(text.split()) * 1.3 for text in batch_texts)
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model,
            usage={
                "prompt_tokens": int(total_tokens),
                "total_tokens": int(total_tokens),
                "cached_embeddings": cached_count,
                "new_embeddings": len(request.texts) - cached_count
            },
            cached=cached_count > 0
        )
        
    except Exception as e:
        logger.error(f"Error in batch embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """
    Calculate cosine similarity between two texts
    """
    try:
        # Get embeddings for both texts
        embedding_request = EmbeddingRequest(
            text=[request.text1, request.text2],
            model=request.model
        )
        
        response = await get_embeddings(embedding_request)
        embeddings = response.embeddings
        
        # Calculate cosine similarity
        embedding1 = np.array(embeddings[0])
        embedding2 = np.array(embeddings[1])
        
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        return SimilarityResponse(
            similarity=float(similarity),
            model=request.model
        )
        
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available embedding models"""
    return {
        "models": [
            {
                "id": "text-embedding-ada-002",
                "description": "OpenAI's text-embedding-ada-002 model",
                "dimensions": 1536
            },
            {
                "id": "text-embedding-3-small",
                "description": "OpenAI's smaller embedding model",
                "dimensions": 1536
            },
            {
                "id": "text-embedding-3-large",
                "description": "OpenAI's larger embedding model",
                "dimensions": 3072
            }
        ]
    }


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return await embedding_cache.get_stats()


@app.post("/cache/clear")
async def clear_cache():
    """Clear the embedding cache"""
    await embedding_cache.clear()
    return {"message": "Cache cleared successfully"}


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add process time header to responses"""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("EMBEDDING_SERVICE_PORT", 8100))
    host = os.getenv("EMBEDDING_SERVICE_HOST", "0.0.0.0")
    
    logger.info(f"Starting Embedding Service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )