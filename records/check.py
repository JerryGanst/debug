from models.query import WholeProcessRecorder
from mongodb.ops.object_op import get_objects_by_conditions

if __name__ == "__main__":
    conditions = {}
    error, records = get_objects_by_conditions(conditions, WholeProcessRecorder, "whole_process_records")
    if error:
        print(error)
        exit()

    for r in records:
        print(f"=====================\n{r}\n=======================\n")
