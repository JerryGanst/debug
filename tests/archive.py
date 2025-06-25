from typing import List

from models.document import Document
from mongodb.ops.object_op import get_objects_by_conditions


def get_unprocessed_pdfs() -> List[Document]:
    conditions = {"processed_to_pages": False, "file_type": "pdf"}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    if error:
        return []
    documents: List[Document]
    return documents
