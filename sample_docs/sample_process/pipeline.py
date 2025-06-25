import logging
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from models.document import Document, Chunk
from mongodb.ops.object_op import (
    get_objects_by_conditions
)
from sample_docs.sample_process.doc_abstract import get_pages_of_document, fill_document_abstract
from sample_docs.sample_process.doc_to_mongodb import add_document_to_mongodb
from sample_docs.sample_process.doc_to_pages import document_to_pages
from sample_docs.sample_process.embedding_process import doc_embed, page_embed, chunk_embed
from sample_docs.sample_process.page_to_chunks import chunk_for_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from configs.load import load_config
config = load_config()
WEAVIATE_BASE_URL = config.get("context_retrieval").get("weaviate_endpoint")
# WEAVIATE_BASE_URL = "http://127.0.0.1:8085"


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass


def process_single_document(
        file_path: str,
        enforce_reprocess: bool = False
) -> Tuple[bool, Optional[Document]]:
    """
    Process a single document through the entire pipeline.
    Returns (success, document) tuple.
    """
    logger.info("=========================================================================")
    logger.info(f"###STARTING_DOCUMENT: {file_path}")
    try:
        # Step 1: Add document to MongoDB
        logger.info(f"Adding document to MongoDB: {file_path}")
        document = add_document_to_mongodb(file_path)
        if not document:
            raise ProcessingError(f"Failed to add document to MongoDB: {file_path}")

        # Step 2: Split document into pages
        if not document.processed_to_pages or enforce_reprocess:
            logger.info(f"Splitting document into pages: {document.title}")
            pages = document_to_pages(document)
            if not pages:
                raise ProcessingError(f"Failed to split document into pages: {document.title}")

        # step 2.1
        if not document.abstract:
            logger.info(f"step 2.1 --> fill_document_abstract: {document.title}")
            fill_document_abstract(document)

        # Step 3: Generate embeddings for document and pages
        if not document.abstract_embedding or enforce_reprocess:
            logger.info(f"Generating document embedding: {document.title}")
            doc_embed(document)

        pages = get_pages_of_document(document)
        for page in pages:
            if not page.abstract_embedding or enforce_reprocess:
                logger.info(f"Generating embedding for page {page.page_num}")
                page_embed(page)

        # Step 4: Generate chunks and their embeddings
        logger.info(f"Generating chunks for document: {document.title}")
        chunk_for_document(document, enforce_reprocess)

        # Get all chunks for the document
        error, chunks = get_objects_by_conditions(
            {"document_id": document.id},
            Chunk,
            "chunks"
        )
        if error:
            raise ProcessingError(f"Failed to retrieve chunks: {error}")

        # Generate embeddings for chunks
        for chunk in chunks:
            if not chunk.chunk_embedding or enforce_reprocess:
                logger.info(f"Generating embedding for chunk {chunk.id}")
                chunk_embed(chunk)

        # Step 5: Insert into Weaviate
        logger.info("Inserting document into Weaviate")
        resp = requests.post(
            f"{WEAVIATE_BASE_URL}/v1/document/insert",
            json=document.model_dump()
        )
        if resp.status_code != 200:
            raise ProcessingError(f"Failed to insert document into Weaviate: {resp.text}")

        for page in pages:
            logger.info(f"Inserting page {page.page_num} into Weaviate")
            resp = requests.post(
                f"{WEAVIATE_BASE_URL}/v1/page/insert",
                json=page.model_dump()
            )
            if resp.status_code != 200:
                raise ProcessingError(f"Failed to insert page into Weaviate: {resp.text}")

        for chunk in chunks:
            logger.info(f"Inserting chunk {chunk.id} into Weaviate")
            resp = requests.post(
                f"{WEAVIATE_BASE_URL}/v1/chunk/insert",
                json=chunk.model_dump()
            )
            if resp.status_code != 200:
                raise ProcessingError(f"Failed to insert chunk into Weaviate: {resp.text}")

        logger.info(f"Successfully processed document: {document.title}")
        logger.info(f"###END_DOCUMENT: {file_path}")
        logger.info("=========================================================================")
        return True, document

    except Exception as e:
        logger.error(f"Error processing document {file_path}: {str(e)}")
        logger.error(f"###END_DOCUMENT: {file_path}")
        logger.info("=========================================================================")
        return False, None


def process_directory(
        directory_path: str,
        file_types: List[str] = ['.pdf', '.docx', '.doc', '.pptx', '.ppt'],
        enforce_reprocess: bool = False
) -> List[Tuple[str, bool]]:
    """
    Process all documents in a directory.
    Returns list of (file_path, success) tuples.
    """
    results = []
    directory = Path(directory_path)

    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")

    for file_type in file_types:
        for file_path in directory.glob(f"*{file_type}"):
            logger.info(f"Processing file: {file_path}")
            success, _ = process_single_document(str(file_path), enforce_reprocess)
            results.append((str(file_path), success))

    return results


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <file_or_directory_path> [--enforce-reprocess]")
        sys.exit(1)

    path = sys.argv[1]
    enforce_reprocess = "--enforce-reprocess" in sys.argv

    if Path(path).is_file():
        success, doc = process_single_document(path, enforce_reprocess)
        print(f"Processing {'succeeded' if success else 'failed'} for {path}")
    else:
        results = process_directory(path, enforce_reprocess=enforce_reprocess)
        for file_path, success in results:
            print(f"Processing {'succeeded' if success else 'failed'} for {file_path}")

'''
# Process a single file
python pipeline.py /path/to/document.pdf

# Process a directory
python pipeline.py /path/to/directory

# Force reprocessing
python pipeline.py /path/to/document.pdf --enforce-reprocess


python -m sample_docs.sample_process.pipeline /root/ns-rag/sample_docs/batch2 >batch2.log 2>&1

python -m sample_docs.sample_process.pipeline /root/ns-rag/sample_docs/batch2/LXJS-QWI-GM-01__1_立讯技术公务接待管理办法__1_.pdf
'''
