from models.document import Chunk, Document, Page
from mongodb.ops.object_op import get_objects_by_conditions


def check_data_integrity(documents, pages, chunks):
    """
    Checks the integrity of data given lists of documents, pages, and chunks.

    Integrity conditions:
    1. Each document must have at least one associated page and one associated chunk.
    2. Every page and chunk must reference an existing document.

    Args:
        documents (list): List of Document objects.
        pages (list): List of Page objects.
        chunks (list): List of Chunk objects.
    """
    issues = []

    # Create a set of document ids from the documents list
    document_ids = {doc.id for doc in documents}

    # Verify that each document has corresponding pages and chunks
    for doc in documents:
        pages_count = sum(1 for page in pages if page.document_id == doc.id)
        chunks_count = sum(1 for chunk in chunks if chunk.document_id == doc.id)
        if pages_count == 0:
            issues.append(f"Document {doc.id} - {doc.title} has no associated pages.")
        elif pages_count != doc.pages:
            issues.append(f"Document {doc.id} - {doc.title} has wrong pages: doc.pages={doc.pages}, pages={pages_count}.")
        if chunks_count == 0:
            issues.append(f"Document {doc.id} - {doc.title} has no associated chunks.")

    # Check for orphan pages (pages that reference non-existent documents)
    for page in pages:
        if page.document_id not in document_ids:
            issues.append(f"Page {page.id} references non-existent document {page.document_id}.")
        if "空的" in page.page_text:
            print(page.document_id, page.page_text)

    # Check for orphan chunks (chunks that reference non-existent documents)
    for chunk in chunks:
        if chunk.document_id not in document_ids:
            issues.append(f"Chunk {chunk.id} references non-existent document {chunk.document_id}.")

    # Report findings
    if issues:
        print("Data integrity issues found:")
        for issue in issues:
            print(" -", issue)
    else:
        print("Data integrity check passed: no issues found.")


# Example usage:

    # Example usage with your get_objects_by_conditions function:
if __name__ == "__main__":
    error, chunks = get_objects_by_conditions({}, Chunk, "chunks")
    if error:
        print(error)
        exit()

    error, pages = get_objects_by_conditions({}, Page, "pages")
    if error:
        print(error)
        exit()

    error, documents = get_objects_by_conditions({}, Document, "documents")
    if error:
        print(error)
        exit()

    # Now run the integrity check with the retrieved records.
    check_data_integrity(documents, pages, chunks)
