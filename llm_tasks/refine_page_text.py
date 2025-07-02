from openai import OpenAI
from configs.load import load_config,ModelRouter

config = load_config()
router = ModelRouter(config)

def refine_text_with_llm(original_text: str):
    # print(f"REFINE PAGE TEXT-ORIGINAL: {original_text}")
    prompt = f"""
            # 角色设定：
            你是一个高级文本处理模型，你的任务是优化给定文本，并保持其原意。
            
            ## 处理要求：
            1. **仅保留有意义的内容**：
               - **保留所有中文和英文文本**。
               - **保留日期信息**（例如："2024-01-15"、"January 15, 2024"、"15 Jan 2024"）。
               - **必要的标点符号可以保留**，以确保文本清晰易读。
               - **删除特殊符号、多余空格、无意义字符**（如："......"、"###"、"———"、"@@@"）。
               - **删除无关字符**（如 "- 3 -" 这样的页码，或者表格填充符号）。
               - **保留文本结构**（如编号列表）。
            
            2. **确保文本清晰 & 保持原文表述**：
               - **不得** 改写、润色或改变任何句子的原意。
               - **不得** 对文本进行总结或重写，只需去除无意义内容。
               - 只删除 **无意义部分**，但保留 **句子原结构**。
            
            ---
            
            ## 处理示例：
            ### **示例输入**
            2024-01-15 这 是一个示例! ——
            一些无用的@@@字符……例如：###， 还有一些———无意义的符号和空格。 另外，时间格式 15 Jan 2024 应该保留。
            
            ### **期望输出**
            2024-01-15 这 是一个示例! 一些无用的字符，例如： 另外，时间格式 15 Jan 2024 应该保留。
            
                        
            ---
            
            ## **待处理文本**
            请按照上述要求处理以下文本：
            ####待处理文本开始####
            {original_text}
            ####待处理文本结束####
            
            ## 注意：如果待处理文本是乱码，直接返回"本页内容为乱码"
        """


    openai_api_base = router.get_model_config("refine_page_text").get("endpoint")
    openai_api_key = router.get_model_config("refine_page_text").get("key", "SOME_KEY")
    thinking = router.get_model_config("refine_page_text").get("thinking")
    
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
        temperature=0.0,
        # stream=True  # 启用流式输出
        extra_body={
            "chat_template_kwargs": {"enable_thinking": thinking},
    },
    )
    refined_text = response.choices[0].message.content.strip()
    # refined_text = ""
    # for chunk in response:
    #     if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
    #         print(chunk.choices[0].delta.content, end="", flush=True)  # 实时打印
    #         refined_text += chunk.choices[0].delta.content  # 逐步拼接文本
    #
    # print()  # 打印换行，确保完整显示
    return refined_text


if __name__ == "__main__":
    t = refine_text_with_llm(
        '''
        \n            连接创新  成就未来\n系统名称：\nQuality Name ： 主题：\nObject： 编号：\nNO.： AHR0 21\n管理系 统\nManagement system  导师管理办法  版次：\nREV.： V1.0 页数：\nPage： 4 / 7\n本文件之著作权及业务秘密内容属于立讯公司，非经准许不得翻印\nThis document is the sole property of Luxshare. And should not be used in whole or in part without prior written permission.\n4. 导师制运行流程\n        
        '''
    )
    print(t)
