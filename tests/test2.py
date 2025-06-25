from configs.load import load_config

if __name__ == "__main__":
    config = load_config()

    # embedding模型的接口
    print("embedding模型的接口:")
    print(config.get("context_retrieval").get("embedding_endpoint"))
    # weaviate向量数据库的接口
    print("weaviate向量数据库的接口:")
    print(config.get("context_retrieval").get("weaviate_endpoint"))
    # doc_metadata
    print("doc_metadata:")
    print(config.get("doc_metadata").get("endpoint"))
    # document_abstract
    print("document_abstract:")
    print(config.get("document_abstract").get("endpoint"))
    # page_abstract
    print("page_abstract:")
    print(config.get("page_abstract").get("endpoint"))
    # refine_page_text
    print("refine_page_text:")
    print(config.get("refine_page_text").get("endpoint"))
    # mongodb_connection_string
    print("mongodb_connection_string:")
    print(config.get("mongodb").get("mongodb_connection_string"))