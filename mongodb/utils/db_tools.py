from pymongo import ASCENDING, DESCENDING
from mongodb.utils.mongodb import get_client


def create_index():
    client = get_client()
    db = client['reading_club']
    collection = db['book_process_tasks']
    index_name = collection.create_index([('slug', DESCENDING)], unique=True)
    print("Index created:", index_name)

    print(f"\n当前所有indexes：")
    indexes = collection.list_indexes()
    for index in indexes:
        print(index)


if __name__ == "__main__":
    create_index()
