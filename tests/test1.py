from models.document import Chunk
from mongodb.ops.object_op import get_objects_by_conditions

doc_id = "b4ad9a6e-c6a6-4126-86c8-879b88ee8cda"

if __name__ == "__main__":
    conditions = {"document_id": doc_id}
    error, chunks = get_objects_by_conditions(conditions, Chunk, "chunks")
    if error:
        print(error)
        exit()

    print(chunks)