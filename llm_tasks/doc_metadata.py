from openai import OpenAI

from agents.ask_agent import ask_local_agent
from models.document import Document, DocumentMetaData
from mongodb.ops.object_op import get_object_by_id, get_objects_by_conditions
from sample_docs.sample_process.doc_abstract import get_pages_of_document
from configs.load import load_config,ModelRouter
config = load_config()
router = ModelRouter(config)

def generate_document_metadata(document: Document, pages_to_use=3):
    pages = get_pages_of_document(document)
    document_content = "\n".join([f"第{page.page_num}页：{page.page_text}" for page in pages[:pages_to_use]])

    prompt = f"""
    你是一名智能助手，负责从文档信息中提取元数据。根据提供的文档文件名、摘要和前几页的文本内容，提取以下元数据字段，并以 JSON 格式返回：

    1. **title**（str）：文档的标题。如果未明确提供，可以从文件名、摘要或文档内容中推测。
    2. **publish_date**（str，可选，ISO 8601 格式）：如果文档中提到了发布时间，提取该日期。如果存在多个日期，选择最相关的一个。
    3. **author**（str，可选）：如果文档中提到了作者或文档发布机构，提取作者姓名或发布机构名称。
    4. **keywords**（list[str]，可选）：基于摘要和文档内容提取 **能够准确反映文档性质和核心内容** 的关键词。这些关键词应涵盖文档的主题、专业领域、核心概念、关键术语，确保有助于 **检索和分类**。避免过于宽泛的词汇，优先使用文档中明确出现的专业术语。
    5. **outdated**（bool）：判断文档是否过时，可以基于发布日期或内容推测。

    ### 输入：
    - **document_filename**：{document.title}
    - **document_abstract**：{document.abstract}
    - **document_content**：{document_content}

    ### 输出（JSON 格式）：
    返回一个包含提取出的元数据的 JSON 对象。

    示例：
    {{
      "title": "深入理解机器学习",
      "publish_date": "2021-07-15",
      "author": "张三",
      "keywords": ["机器学习", "人工智能", "深度学习"],
      "outdated": false
    }}

    请分析提供的输入并生成 JSON 格式的元数据。
    """

    openai_api_base = router.get_model_config("doc_metadata").get("endpoint")
    openai_api_key = router.get_model_config("doc_metadata").get("key", "SOME_KEY")
    temperature = router.get_model_config("doc_metadata").get("temperature")

    return ask_local_agent(prompt, response_type=DocumentMetaData, api_key=openai_api_key,
                           api_base=openai_api_base, temperature=temperature).get("answer")


if __name__ == "__main__":
    conditions = {}
    error, documents = get_objects_by_conditions(conditions, Document, "documents")
    for doc in documents:
        data =generate_document_metadata(doc)
        print(data)