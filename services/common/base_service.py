"""
Base service class with common functionality for domain-specific services
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
import time
import traceback
from typing import Optional, Dict, Any
import os
import sys
from datetime import datetime
import asyncio
from functools import lru_cache
import redis
import json

# Add parent directory to path to import from existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from routes.chat import ChatRequest, chat_stream, chat_non_stream
from models.query import QueryRequest, WholeProcessRecorder, RecordQueryParams
from routes.summarization import SummaryResponse, summarize
from routes.translation import translate, TranslationRequest
from routes.prompt_filler import prompt_filler, AgentConfig
from routes.similarity import SimilarityRequest, SimilarityResponse, get_embedding, cosine_similarity
from routes.personal_knowledge_base.rag_pipeline import router as personal_rag
from tokenizer_service import TokenCounter
from stream_processor import stream_response
from configs.load_env import settings
from mongodb.ops.object_op import get_objects_by_conditions
from domains.context import DomainContext
from .error_reporting import ErrorReporter, ErrorMiddleware
from .performance import perf_monitor, timed_operation
from .glossary_manager import add_glossary_routes

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'service_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

# Redis for caching (optional, can be disabled)
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None


class BaseService:
    """Base service class with common functionality"""
    
    def __init__(self, domain_name: str, port: int, host: str = "0.0.0.0"):
        self.domain_name = domain_name
        self.port = port
        self.host = host
        self.logger = logging.getLogger(f"{domain_name}Service")
        self.token_counter = TokenCounter()
        self.error_reporter = ErrorReporter(f"{domain_name}Service")
        self.app = None
        self._setup_app()
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage application lifecycle"""
        # Startup
        self.logger.info(f"Starting {self.domain_name} service on port {self.port}")
        # Initialize domain context
        DomainContext.initialize(self.domain_name)
        yield
        # Shutdown
        self.logger.info(f"Shutting down {self.domain_name} service")
        
    def _setup_app(self):
        """Setup FastAPI application with middleware and routes"""
        self.app = FastAPI(
            title=f"{self.domain_name} Service API",
            version="2.0.0",
            lifespan=self.lifespan
        )
        
        # Add middleware
        self._add_middleware()
        
        # Add routes
        self._add_routes()
        
        # Add exception handlers
        self._add_exception_handlers()
        
    def _add_middleware(self):
        """Add middleware for performance and monitoring"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # GZip compression for responses
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Request timing middleware
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            self.logger.info(f"Request: {request.method} {request.url.path} - Time: {process_time:.3f}s")
            return response
        
        # Error tracking middleware with enhanced reporting
        @self.app.middleware("http")
        async def error_tracking_middleware(request: Request, call_next):
            try:
                response = await call_next(request)
                return response
            except Exception as e:
                # Report error with context
                context = self.error_reporter.create_error_context(
                    request_id=getattr(request.state, 'request_id', 'unknown'),
                    endpoint=str(request.url),
                    method=request.method
                )
                self.error_reporter.report_error(e, context=context)
                
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": "Internal server error", "detail": str(e)}
                )
    
    def _add_routes(self):
        """Add common routes to the application"""
        app = self.app
        
        # Include personal RAG router
        app.include_router(personal_rag, prefix="/personal")
        
        # Add glossary management routes
        add_glossary_routes(app, self.domain_name)
        
        # Health check endpoint
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": self.domain_name,
                "timestamp": datetime.utcnow().isoformat(),
                "redis_available": REDIS_AVAILABLE
            }
        
        # Domain info endpoint
        @app.get("/domain-info")
        async def domain_info():
            domain_config = DomainContext.get_config()
            return {
                "domain_name": domain_config.DOMAIN_NAME,
                "doc_type": domain_config.DOMAIN_DOC_TYPE,
                "custom_config": domain_config.custom_config,
            }
        
        # Chat endpoint with caching
        @app.post("/chat")
        async def process_chat(request: ChatRequest):
            # Token validation
            if request.messages:
                if request.file is not None:
                    formatted_files = "\n\n".join(
                        f"文件{i + 1}：\n{content}" for i, content in enumerate(request.file)
                    )
                    request.messages[-1].content += (
                        "\n\n#####用户提供的文件内容开始#####\n\n"
                        f"{formatted_files}\n\n"
                        "#####用户提供的文件内容结束#####\n\n"
                    )
                
                last_message = request.messages[-1].dict()
                token_count = self.token_counter.count_text(last_message["content"])
                if token_count > self.token_counter.token_limit:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "输入token超过限制",
                            "token_count": token_count,
                            "token_limit": self.token_counter.token_limit
                        }
                    )
            
            # Check cache for non-streaming requests
            if not request.stream and REDIS_AVAILABLE:
                cache_key = self._generate_cache_key("chat", request.dict())
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    self.logger.info("Returning cached chat response")
                    return JSONResponse(content=cached_response)
            
            # Process request
            if request.stream:
                return StreamingResponse(
                    chat_stream(request),
                    media_type="text/event-stream"
                )
            else:
                response = await chat_non_stream(request)
                # Cache the response
                if REDIS_AVAILABLE:
                    self._cache_response(cache_key, response)
                return response
        
        # Query endpoint
        @app.post("/query")
        async def process_query(request: QueryRequest):
            token_count = self.token_counter.count_text(request.question)
            if token_count > self.token_counter.token_limit:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "输入token超过限制",
                        "token_count": token_count,
                        "token_limit": self.token_counter.token_limit
                    }
                )
            
            return StreamingResponse(stream_response(request), media_type="text/event-stream")
        
        # Summarize endpoint with caching
        @app.post("/summarize", response_model=SummaryResponse)
        async def process_summary(request: QueryRequest):
            token_count = self.token_counter.count_text(request.question)
            if token_count > self.token_counter.token_limit:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "输入token超过限制",
                        "token_count": token_count,
                        "token_limit": self.token_counter.token_limit
                    }
                )
            
            # Check cache
            if REDIS_AVAILABLE:
                cache_key = self._generate_cache_key("summarize", request.dict())
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    self.logger.info("Returning cached summary")
                    return SummaryResponse(**cached_response)
            
            response = summarize(request)
            
            # Cache the response
            if REDIS_AVAILABLE:
                self._cache_response(cache_key, response.dict())
            
            return response
        
        # Translation endpoint
        @app.post("/translate")
        async def process_translation(request: TranslationRequest):
            SUPPORTED_LANGUAGES = ["中文", "英文", "越南语", "西班牙语"]
            
            if request.target_language not in SUPPORTED_LANGUAGES:
                error_message = f"不支持的语种: {request.target_language}。支持的语种有: {', '.join(SUPPORTED_LANGUAGES)}"
                return JSONResponse(status_code=400, content={"error": error_message})
            
            token_count = self.token_counter.count_text(request.source_text)
            if token_count > self.token_counter.token_limit:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "输入token超过限制",
                        "token_count": token_count,
                        "token_limit": self.token_counter.token_limit
                    }
                )
            
            return StreamingResponse(translate(request), media_type="text/event-stream")
        
        # Similarity endpoint with caching
        @app.post("/similarity", response_model=SimilarityResponse)
        async def calculate_similarity(request: SimilarityRequest):
            # Check cache
            if REDIS_AVAILABLE:
                cache_key = self._generate_cache_key("similarity", request.dict())
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    self.logger.info("Returning cached similarity score")
                    return SimilarityResponse(**cached_response)
            
            # Calculate embeddings in parallel for better performance
            embedding_tasks = [
                asyncio.create_task(asyncio.to_thread(get_embedding, request.str1)),
                asyncio.create_task(asyncio.to_thread(get_embedding, request.str2))
            ]
            embeddings = await asyncio.gather(*embedding_tasks)
            
            similarity_score = cosine_similarity(embeddings[0], embeddings[1])
            response = SimilarityResponse(score=similarity_score)
            
            # Cache the response
            if REDIS_AVAILABLE:
                self._cache_response(cache_key, response.dict())
            
            return response
        
        # Prompt filler endpoint
        @app.post("/prompt_fill")
        async def process_prompt(config: AgentConfig):
            token_count = self.token_counter.count_text(config.agent_description)
            if token_count > self.token_counter.token_limit:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "输入token超过限制",
                        "token_count": token_count,
                        "token_limit": self.token_counter.token_limit
                    }
                )
            
            if config.agent_description == '':
                config = AgentConfig(
                    agent_name=config.agent_name,
                    agent_role=config.agent_role,
                    agent_tone=config.agent_tone
                )
            if config.agent_tone == '':
                config = AgentConfig(
                    agent_name=config.agent_name,
                    agent_role=config.agent_role,
                    agent_description=config.agent_description
                )
            
            return prompt_filler(config)
        
        # Token counting endpoint
        @app.post("/count-tokens")
        async def count_tokens(request: dict):
            if "text" in request:
                token_count = self.token_counter.count_text(request["text"])
                return {
                    "token_count": token_count,
                    "character_count": len(request["text"]),
                    "token_limit": self.token_counter.token_limit
                }
            elif "messages" in request:
                token_count = self.token_counter.count_chat(request["messages"])
                char_count = sum(len(msg.get("content", "")) for msg in request["messages"])
                return {
                    "token_count": token_count,
                    "character_count": char_count,
                    "token_limit": self.token_counter.token_limit
                }
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": "请求格式错误，应包含'text'或'messages'字段"}
                )
        
        # Records endpoint
        @app.post("/get_records")
        async def get_whole_process_records(request: RecordQueryParams):
            conditions = {
                "start_time": {
                    "$gte": request.start_time,
                    "$lte": request.end_time
                }
            }
            error, records = get_objects_by_conditions(
                conditions, WholeProcessRecorder, "whole_process_records"
            )
            if error:
                return {"error": error}
            
            result = []
            for r in records:
                d = r.model_dump()
                d["domain"] = self.domain_name
                result.append(d)
            return result
        
        # Test error endpoint
        @app.get("/test_error")
        def test_error_endpoint():
            raise HTTPException(
                status_code=500,
                detail="这是用于测试抛出异常的例子"
            )
        
        # Performance metrics endpoint
        @app.get("/metrics")
        async def get_performance_metrics():
            """Get performance metrics for monitoring"""
            return {
                "service": self.domain_name,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": perf_monitor.get_metrics(),
                "redis_available": REDIS_AVAILABLE
            }
    
    def _add_exception_handlers(self):
        """Add exception handlers for better error reporting"""
        @self.app.exception_handler(ValueError)
        async def value_error_handler(request: Request, exc: ValueError):
            self.logger.error(f"ValueError: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid input", "detail": str(exc)}
            )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            self.logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            self.logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "服务器内部错误，请稍后再试"}
            )
    
    def _generate_cache_key(self, prefix: str, data: dict) -> str:
        """Generate a cache key from request data"""
        data_str = json.dumps(data, sort_keys=True)
        return f"{self.domain_name}:{prefix}:{hash(data_str)}"
    
    def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response from Redis"""
        if not REDIS_AVAILABLE:
            return None
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            self.logger.warning(f"Cache get error: {str(e)}")
        return None
    
    def _cache_response(self, key: str, data: Any, ttl: int = 3600):
        """Cache response in Redis with TTL"""
        if not REDIS_AVAILABLE:
            return
        try:
            if hasattr(data, 'dict'):
                data = data.dict()
            redis_client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            self.logger.warning(f"Cache set error: {str(e)}")
    
    def run(self):
        """Run the service"""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    },
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    },
                },
                "root": {
                    "level": "INFO",
                    "handlers": ["default"],
                },
            }
        )