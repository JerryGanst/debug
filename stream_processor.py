import asyncio
from typing import AsyncGenerator, List

from agents.commercial_api_answer import commercial_api_answer
from configs.load import load_config
from models.query import QueryRequest, StreamResponse, ContextSource, WholeProcessRecorder,Answer
from agents.answer_evaluation import evaluate_answer
from agents.answer_generation import generate_answer
from agents.context_retrieval import retrieve_context
from agents.question_classification import classify_question
from agents.question_optimization import optimize_question
from mongodb.ops.object_op import insert_object
from configs.load import ModelRouter
from domains.context import DomainContext

async def stream_response(request: QueryRequest) -> AsyncGenerator[str, None]:
    if not request.question.strip():
        yield StreamResponse(type="error", content="Error: Question cannot be empty.").json()
        return

    CONFIG = load_config()
    # 模型路由
    router = ModelRouter(CONFIG)
    whole_process_recorder = WholeProcessRecorder()
    whole_process_recorder.request = request

    # Helper function to create formatted stream response
    def create_stream_response(type: str, content: str, sources: List[ContextSource] = None) -> str:
        response_data = StreamResponse(type=type, content=content, sources=sources).model_dump_json()
        return f"data: {response_data}\n\n"

    yield create_stream_response('process', '开始处理请求...')

    # Step 0： 对问题进行分类
    yield create_stream_response("process", "[Start] 开始对问题进行分类...")

    classification_result = await asyncio.to_thread(classify_question, request.question,
                                                    router.get_model_config("question_classification"))
    question_category = classification_result.get("answer").get("category")
    classification_reason = classification_result.get("answer").get("reason")
    whole_process_recorder.question_category = question_category
    whole_process_recorder.classification_reason = classification_reason
    
    # 从当前领域配置直接获取问题分类描述
    domain_config = DomainContext.get_config()
    question_categories = domain_config.get_question_categories()
    
    yield create_stream_response("process",
                                 f"[End] 问题的类别为：{question_category}: {question_categories.get(question_category)}\n分类原因：{classification_reason}")

    # if question_category == 3:
    #     yield create_stream_response("final_answer", "无关问题，不予回答...")
    #     return
    #
    # if question_category == 3:
    #     yield create_stream_response("process", "[Start] 通用问题，将调用商业大模型进行回答...")
    #     response = commercial_api_answer(request.question, CONFIG.get("commercial_api"))
    #     yield create_stream_response("final_answer", response)
    #     return

    optimized_question, info_to_collect = request.question, [request.question]

    #if CONFIG.get("question_optimization").get("enable"):
    if router.get_module_config("question_optimization").get("enable"):
        # Step 1: 对问题进行优化 (optional)
        yield create_stream_response("process", f"[Start] 开始对问题进行优化...")

        optimized_question_data = await asyncio.to_thread(optimize_question, request.question, question_category,
                                                          router.get_model_config("question_optimization"))

        optimized_question = optimized_question_data.get("answer").get("optimized_question", request.question)
        info_to_collect = optimized_question_data.get("answer").get("info_to_collect", [])
        info_to_collect_str = "\n".join([f"  - {info}" for info in info_to_collect])

        whole_process_recorder.optimized_question = optimized_question
        whole_process_recorder.info_to_collect = info_to_collect

        yield create_stream_response("process", f"[Result] 优化后的问题: {optimized_question}")
        yield create_stream_response("process", f"[Result] 需要采集的信息: \n{info_to_collect_str}")
        yield create_stream_response("process", f"[End] 已完成问题优化")

    loop_count = 0
    retrieved_contexts = []
    final_answer, final_source = "", ""

    while loop_count < CONFIG.get("max_loop", 1):
        loop_count += 1
        yield create_stream_response("process", f"[Start] 开始第 {loop_count} 轮查询...")

        # Step 2: Retrieve context
        yield create_stream_response("process", f"[Start] 检索资料库...")
        newly_retrieved_contexts = retrieve_context(info_to_collect, question_category, CONFIG.get("context_retrieval"), process_recorder=whole_process_recorder)
        whole_process_recorder.retrieved_contexts = newly_retrieved_contexts
        newly_retrieved_str = "\n".join([f"  - {str(ctx)}" for ctx in newly_retrieved_contexts])
        retrieved_contexts.extend(newly_retrieved_contexts)

        yield create_stream_response("process", f"[Result] 取回资料: \n{newly_retrieved_str}")
        yield create_stream_response("process", f"[End] 完成资料库检索")
        await asyncio.sleep(0.1)

        # Step 3: Generate answer
        yield create_stream_response("process", f"[Start] 开始总结答案...")
        # TODO: generate answer
        final_answer = await asyncio.to_thread(generate_answer, optimized_question, retrieved_contexts,
                                               question_category, router.get_model_config("answer_generation",request.model))

        whole_process_recorder.final_answer = Answer(**final_answer.get("answer"))
        whole_process_recorder.finish()

        error, res = insert_object(whole_process_recorder, "whole_process_records")
        if error:
            print(f"插入数据库错误：{error}\nWholeProcessRecorder:\n{whole_process_recorder}")

        if final_answer.get("answer").get("is_question_answered"):
            answer = final_answer.get("answer").get("answer")
            yield create_stream_response("process", f"[Result] 生成答案: {answer}")
        else:
            answer = final_answer.get("answer").get("answer")
            yield create_stream_response("process", f"[Result] 无法回答: {answer}")

        yield create_stream_response("process", f"[End] 已完成总结答案")

        break
        # # Step 4: Evaluate answer
        # yield create_stream_response("process", "[Start] 开始评估生成的答案...")
        # # TODO Evaluate
        # evaluation_data = evaluate_answer(request.question, optimized_question, retrieved_contexts, question_category,
        #                                   CONFIG.get("answer_evaluation"))
        #
        # evaluation_result = evaluation_data.get("evaluation")
        # evaluation_reason = evaluation_data.get("reason")
        #
        # yield create_stream_response("process", f"[Result] 评估结果: {evaluation_result}, 原因: {evaluation_reason}")
        # yield create_stream_response("process", "[End] 已完成答案评估")
        # await asyncio.sleep(0.1)
        #
        # if evaluation_result:
        #     yield create_stream_response("process", "答案已被接受")
        #     break
        # else:
        #     yield create_stream_response("process", f"答案改进意见 {evaluation_reason}")

    if final_answer.get("answer").get("is_question_answered"):
        if "reasoning" in request.model:
            yield  create_stream_response("reasoning",final_answer.get("reasoning"))
        yield create_stream_response("final_answer", final_answer.get("answer").get("answer"), sources=final_answer.get("answer").get("contexts"))
    else:
        if "reasoning" in request.model:
            yield  create_stream_response("reasoning",final_answer.get("reasoning"))
        yield create_stream_response("final_answer", final_answer.get("answer").get("answer"))
