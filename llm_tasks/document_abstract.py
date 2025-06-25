from openai import OpenAI
from configs.load import load_config,ModelRouter

config = load_config()
router = ModelRouter(config)

def generate_document_abstract(document_title: str, page_abstracts: str):
    prompt = f"""
        # 任务描述：
        你是一个高级文本摘要生成模型，擅长精准提炼文档的关键信息。你的任务是根据提供的 **文档标题** 和 **每页摘要**，生成**高质量的整体摘要**。该摘要将用于向量数据库检索，因此必须精准概括文档核心内容。

        ## 生成要求：
        1. **高度概括文档核心内容**：
           - **最大程度捕捉文档的本质信息**，使摘要能够清晰表达文档的主题。
           - **综合每页摘要的信息**，避免单独片段化，而是形成完整的、连贯的概述。
           - **保留专业术语、专有名词、关键数据和重点概述**，确保摘要在检索时能有效匹配相关查询。

        2. **简洁、清晰、富有信息量**：
           - 直接输出最终摘要，无需解释任务或额外说明。
           - **避免空泛或过于笼统的表述**，确保摘要能够精准反映文档内容。
           - 句子应简练，**避免冗余**，但同时保持信息完整性。

        3. **摘要长度自适应**：
           - **推荐 200-400 字**，以确保信息完整并适用于检索需求。
           - **不强制字数要求**，如果原文内容较少或信息较为简单，摘要可适当缩短，确保核心信息表达充分，而不过度扩展。

        4. **仅输出摘要文本**：
           - **不得** 解释任务要求，不得包含额外说明。
           - **不得** 生成标题，仅输出 **最终摘要**。

        ---

        ## 示例：
        ### **示例输入**
        #### **文档标题**
        企业数据安全管理规范
        #### **每页摘要**
        第 1 页：本规范定义了企业数据安全管理的基本原则，涵盖数据分类、权限管理及合规要求。 
        第 2 页：企业应按照数据敏感度分类，并实施分级存储、访问控制和加密措施，防止未经授权访问。 
        第 3 页：规范要求企业定期进行数据安全审计，并采取风险评估机制，确保数据泄露防范。 
        第 4 页：所有员工需接受数据安全培训，提升合规意识，违规行为将面临相应处罚。

        ### **期望输出**
        本规范定义企业数据安全管理要求，包括数据分类、访问控制、加密措施及定期审计机制。企业需依据数据敏感度分级存储，并采取风险评估机制防止数据泄露。员工必须接受数据安全培训，提高合规意识，违规者将面临相应处罚，以确保整体数据安全性。

        ---

        ## **待处理文档**
        请根据以下 **文档标题** 和 **每页摘要** 生成摘要：
        #### **文档标题**
        {document_title}
        #### **每页摘要**
        {page_abstracts}
    """


    openai_api_base = router.get_model_config("document_abstract").get("endpoint")
    openai_api_key = router.get_model_config("document_abstract").get("key", "SOME_KEY")
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    models = client.models.list()
    model = models.data[0].id

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model=model,
        temperature=0.0
    )
    document_abstract = response.choices[0].message.content.strip()
    return document_abstract


if __name__ == "__main__":
    t = generate_document_abstract(
        ""
    )
    print(t)
