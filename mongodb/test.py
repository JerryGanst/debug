# 插入数据测试
from datetime import datetime
from models.document import Document, FileType, DocumentType
from mongodb.ops.object_op import insert_object, get_objects_by_conditions


# 插入文档实例到数据库
def insert_document_example():
    try:
        # 创建 Document 实例
        document = Document(
            title="Sample HR Rules Document",
            file_type=FileType.PDF,
            doc_type=DocumentType.HR_RULES,
            publish_date=datetime.now(),
            author="HR Department",
            file_path="/documents/hr_rules.pdf",
            pages=15,
            file_size=102400,
            language="en"
        )

        # 使用 insert_object 插入数据
        error, res = insert_object(document, collection_name="documents")
        if error:
            print(f"插入失败: {error}")
        else:
            print(f"插入成功，文档 ID: {res}")
    except Exception as e:
        print(f"插入文档时出错: {str(e)}")


def get_documents_by_condition_example():
    try:
        conditions = {
            # "id": "2b65f344-3d4d-4897-8844-32733952bba8",  # 查询 PDF 文件
            "doc_type": DocumentType.HR_RULES  # 查询 HR RULES 类型的文档
        }

        # 使用 get_objects_by_conditions 查询符合条件的文档
        error, documents = get_objects_by_conditions(conditions, obj_class=Document, collection_name="documents", limit=5)
        if error:
            print(f"查询失败: {error}")
        else:
            print(f"查询成功，找到 {len(documents)} 个文档：")
            for doc in documents:
                print(f"文档标题: {doc.title}, 类型: {doc.file_type}, 作者: {doc.author}")
    except Exception as e:
        print(f"查询文档时出错: {str(e)}")


if __name__ == "__main__":

    # 示例：插入文档
    #insert_document_example()

    # 示例：根据条件查询文档
    get_documents_by_condition_example()

