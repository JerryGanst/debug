import requests
import json
import yaml
import os
import sys
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel
from openai import OpenAI


class Evaluation(BaseModel):
    score: float
    evaluation_detail: list[str]


def load_config():
    with open("./evaluation_config.yaml", "r") as file:
        return yaml.safe_load(file)


def query_documents(titles: list, config: dict):
    resp = requests.post(f"{config.get('weaviate_endpoint')}/v1/document/get_documents_by_filters",
                         json={'document_titles': titles})

    assert resp.status_code == 200, "query document failed {resp.text}"

    return {doc_item['title'] for doc_item in resp.json()}


def llm_evaluation(question: str, final_answer: dict, model_answer, config: dict):
    prompt = f"""
        你是一个专业的 HR 知识问答评估助手，任务是根据用户问题对知识库提供的答案与标准答案进行比对和评分。请仔细阅读用户问题、知识库的答案和标准答案，然后根据以下要求进行评估：

        ### 任务说明
        1. **准确性评估（40%）：** 检查知识库答案是否在事实、细节和关键信息点（如政策年份、地区适用性、特定法规条款等）上与标准答案一致。
        2. **完整性评估（30%）：** 判断知识库答案是否覆盖了标准答案中提到的所有核心信息，避免遗漏关键要点。
        3. **专业性评估（20%）：** 分析答案的语言表达是否专业、准确，并符合 HR 领域的术语和表达习惯。
        4. **条理性评估（10%）：** 评估答案是否结构清晰，逻辑合理，便于理解。
        5. **引用准确性：** 如果答案引用了上下文或来源，检查引用是否准确且恰当。
        
        ### 评分标准
        - **准确性（40%）**
        - **完整性（30%）**
        - **专业性（20%）**
        - **条理性（10%）**
        
        ### 最终评分
        请基于以上各项指标，计算一个综合得分（0到1之间）。
        
        ### 注意
        - **最终评分基于以上各项指标，范围在0到1之间。**
        - **必须对以上四个维度逐一进行评估，不能遗漏。**
        - 如果某个维度没有问题，也要明确写出“无问题”或“符合要求”。
        
        ### 用户问题
        {question}
        
        ### 知识库答案
        {final_answer}
        
        ### 标准答案
        {model_answer}
        
        ### 输出格式
        请以 JSON 格式输出评估结果，**确保每一个维度都有对应的描述**:
        
        ```json
        {{
            "score": 0.9,
            "evaluation_details": [
                "准确性评估：描述与标准答案的一致性或差异",
                "完整性评估：描述是否遗漏关键信息",
                "专业性评估：描述语言表达的专业性",
                "条理性评估：描述结构和逻辑的清晰度"
            ]
        }}
        ```
        
        ### 自检要求
        - 在生成 JSON 之前，检查是否所有维度都有填写评估细节。
        - 如果某个维度遗漏，必须补全后再输出。
        
        请开始对比知识库答案和标准答案，并输出最终的评估结果。
    """

    openai_api_key = config.get("key")
    openai_api_base = config.get("endpoint")
    thinking = config.get("thinking")

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    models = client.models.list()
    model = models.data[0].id

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model=model,
        temperature=config.get("temperature"),
        extra_body={
            "guided_json": Evaluation.model_json_schema(),
            "chat_template_kwargs": {"enable_thinking": thinking},
        }
    )
    return json.loads(response.choices[0].message.content)


def sources_evaluation(document_title, page, origin_sources):
    source_usage_count = 0
    doc_page_map = {f"{document_title}-{p}": True for p in page.split(',')}

    for source in origin_sources:
        if f"{source['document_title']}-{source['page']}" in doc_page_map:
            source_usage_count += 1
        elif source['document_title'] == document_title:
            source_usage_count += 0.75
    return source_usage_count / len(origin_sources)


def evaluation(question_item, config: dict):
    resp = requests.post(f"{config.get('rag_url')}/query", headers={"Content-Type": "application/json"},
                         json={'question': question_item['question'], 'user_id': '2'}, stream=True)

    final_answer = None
    for line in resp.iter_lines():
        if line:
            process = json.loads(line.decode("utf-8")[6:])
            if process['type'] == 'final_answer':
                final_answer = process
                break

    if not final_answer or not final_answer['sources']:
        return 0

    llm_evaluation_weight = config.get('llm_evaluation_weight', 0.0)
    sources_eval_score = sources_evaluation(question_item['document_title'], question_item['page'],
                                            final_answer['sources'])
    llm_eval_result = llm_evaluation(question_item['question'], final_answer, question_item['answer'], config)
    score = sources_eval_score * (1 - llm_evaluation_weight) + llm_eval_result['score'] * llm_evaluation_weight
    print(f"question: {question_item['question']}, "
          f"score: {score}, "
          f"sources_eval_score: {sources_eval_score}, "
          f"llm_eval_score: {llm_eval_result['score']}, "
          f"llm_evaluation_details: {llm_eval_result['evaluation_detail']}, "
          f"source: {question_item['document_title']}-{question_item['page']}, "
          f"rag_answer_sources: {final_answer['sources']}, "
          f"rag_answer: {final_answer['content']}, "
          f"answer: {question_item['answer']}")

    return score


def query_from_rag(question_item, config: dict):
    lt = time.localtime()
    start_time = time.perf_counter()
    resp = requests.post(f"{config.get('rag_url')}/query", headers={"Content-Type": "application/json"},
                         json={'question': question_item['question'], 'user_id': '2'}, stream=True)

    final_answer = None
    for line in resp.iter_lines():
        if line:
            process = json.loads(line.decode("utf-8")[6:])
            if process['type'] == 'final_answer':
                final_answer = process
                break
    if not final_answer:
        print("haven't receive final answer")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"线程开始时间：{time.strftime('%Y-%m-%d %H:%M:%S', lt)}, 执行耗时: {elapsed_time} 秒")


def eval_question(data):
    pass_score = 0.6
    pass_count = 0
    eval_question_count = 0

    print(f'及格分数为: {pass_score}')
    for question_item in data:
        if not exits_documents_map[question_item['document_title']]:
            continue
        score = evaluation(question_item, configs.get('evaluation'))
        eval_question_count += 1
        if score >= pass_score:
            pass_count += 1
    print(f'及格率为: {pass_count / eval_question_count}')


async def limit_test(data, batch_size, interval, config: dict):
    loop = asyncio.get_running_loop()
    # 使用线程池运行阻塞的 send_request 函数
    with ThreadPoolExecutor() as executor:
        tasks = []
        for i in range(batch_size):
            # 立即调度任务，实际请求耗时在各自线程中运行
            # print(i)
            task = loop.run_in_executor(executor, query_from_rag, data[i % len(data)], config)
            tasks.append(task)
            # 等待指定的间隔时间后再调度下一个请求（不考虑请求实际执行时间）
            await asyncio.sleep(interval)
        # 等待所有任务执行完毕
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("请提供 JSON 文件的路径和执行类型作为命令行参数。")
        sys.exit(1)

    # 获取 JSON 文件路径
    file_path = sys.argv[1]
    exec_type = sys.argv[2]
    batch_size = int(sys.argv[3])
    interval = float(sys.argv[4])

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 解析 JSON 数据
            data = json.load(file)
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到，请检查文件路径。")
    except json.JSONDecodeError:
        print(f"文件 {file_path} 不是有效的 JSON 文件，请检查文件内容。")

    configs = load_config()

    doc_title_list = set()
    for question_item in data:
        question_item['document_title'] = os.path.splitext(question_item['document_title'])[0]
        doc_title_list.add(question_item['document_title'])

    doc_title_list = list(doc_title_list)
    doc_title_map = {dt: True for dt in doc_title_list}

    # 只评估数据库存在的文件
    exits_documents = query_documents(doc_title_list, configs.get('evaluation'))
    # document 表的 title 是 word 分词匹配（weaviate 功能限制导致分词匹配和精确匹配无法同时存在），需要多筛一次得到真实的问题合集里包含的数据库存在的文档
    exits_documents = [ed for ed in exits_documents if ed in doc_title_map]
    exits_documents_map = {ed: True for ed in exits_documents}
    print(f"问题合集涉及 {len(doc_title_list)} 份文档, 数据库存在 {len(exits_documents)} 份文档")

    data = [question_item for question_item in data if exits_documents_map.get(question_item['document_title'])]

    if exec_type == 'limit_test':
        start_time = time.perf_counter()
        asyncio.run(limit_test(data, batch_size, interval, configs.get('evaluation')))
        end_time = time.perf_counter()
        print(f"batch 总耗时：{end_time-start_time} 秒")
        sys.exit(0)
    else:
        eval_question(data)
