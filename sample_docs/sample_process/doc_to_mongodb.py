import os
import logging
from pathlib import Path
from typing import Optional

from models.document import FileType, Document, DocumentType
from mongodb.ops.object_op import insert_object, get_objects_by_conditions
from domains.context import DomainContext

logger = logging.getLogger(__name__)

# 目标文件夹路径（请修改为你的文件夹路径）
folder_path = "../人力资源相关课件及管理办法"


def add_document_to_mongodb(file_path: str) -> Optional[Document]:
    """
    Add a document to MongoDB if it doesn't exist.
    Returns the Document object if successful, None otherwise.
    """
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    file_path = os.path.abspath(file_path)

    # Check if document already exists
    conditions = {"file_path": file_path}
    error, existing_docs = get_objects_by_conditions(conditions, Document, "documents")
    if not error and existing_docs:
        logger.info(f"文件已存在，直接返回：{file_path}")
        return existing_docs[0]

    # Get file information
    path = Path(file_path)
    if not path.exists():
        logger.error(f"文件不存在：{path}")
        return None

    file_ext = path.suffix[1:].lower()  # Remove the dot and convert to lowercase

    # Ensure extension is supported
    if file_ext not in FileType.__members__.values():
        logger.error(f"不支持文件：{file_ext}")
        return None

    file_type = FileType(file_ext)

    # 获取对应领域的文档类型
    try:
        doc_type = getattr(DocumentType, domain_config.DOMAIN_DOC_TYPE)
    except AttributeError:
        # 如果配置的文档类型不存在，则尝试使用字符串值作为枚举值
        try:
            doc_type = DocumentType(domain_config.DOMAIN_DOC_TYPE)
        except ValueError:
            # 如果作为枚举值也失败，则回退到默认值
            logger.warning(f"无法将 {domain_config.DOMAIN_DOC_TYPE} 转换为有效的文档类型，使用IT作为默认值")
            doc_type = DocumentType.IT

    # Create new document
    doc = Document(
        title=path.stem,  # filename without extension
        file_type=file_type,
        doc_type=doc_type,  # 使用配置的领域文档类型
        file_path=file_path,
        file_size=path.stat().st_size,
        processed_to_pages=False
    )

    # Insert into MongoDB
    error, res = insert_object(doc, "documents")
    if error:
        logger.error(f"插入数据库错误：{error}")
        return None

    conditions = {"id": res}
    error, existing_docs = get_objects_by_conditions(conditions, Document, "documents")
    if not error and existing_docs:
        return existing_docs[0]

    logger.error(f"取回插入数据库失败：{error}")
    return None


if __name__ == "__main__":
    # 获取文件列表并创建 Document 对象
    documents = []
    # 获取当前活动的领域配置
    domain_config = DomainContext.get_config()
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_ext = filename.split(".")[-1].lower()

            # 确保扩展名是支持的 FileType
            if file_ext in FileType.__members__.values():
                file_type = FileType(file_ext)
            else:
                continue  # 跳过不支持的文件类型

            # 获取对应领域的文档类型
            try:
                doc_type = getattr(DocumentType, domain_config.DOMAIN_DOC_TYPE)
            except AttributeError:
                # 如果配置的文档类型不存在，则尝试使用字符串值作为枚举值
                try:
                    doc_type = DocumentType(domain_config.DOMAIN_DOC_TYPE)
                except ValueError:
                    # 如果作为枚举值也失败，则回退到默认值
                    print(f"无法将 {domain_config.DOMAIN_DOC_TYPE} 转换为有效的文档类型，使用IT作为默认值")
                    doc_type = DocumentType.IT

            doc = Document(
                title=os.path.splitext(filename)[0],  # 去掉扩展名
                file_type=file_type,
                doc_type=doc_type,  # 使用配置的领域文档类型
                file_path=os.path.abspath(file_path),
                file_size=os.path.getsize(file_path),  # 获取文件大小（字节）
                processed_to_pages=False
            )
            documents.append(doc)

    # 输出结果
    for doc in documents:
        print(doc.model_dump_json(indent=4))
        insert_object(doc, "documents")
