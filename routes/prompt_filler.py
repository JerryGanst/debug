from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from configs.load import load_config,ModelRouter

config = load_config()
router = ModelRouter(config)

class AgentConfig(BaseModel):
    agent_name: str = Field(..., description = "智能体名称")
    agent_role: str = Field(..., description = "智能体角色")
    agent_tone: str = Field(default = '轻松', description="智能体语气")
    agent_description: str = Field(default = '用户未提供智能体设定，请根据已有信息判断', description = "智能体设定")
    
def prompt_filler(agent_config: AgentConfig):
    agent_name = agent_config.agent_name
    agent_role = agent_config.agent_role
    agent_tone = agent_config.agent_tone
    agent_description = agent_config.agent_description
    
    system_prompt = f'''
    - Role: 提示词优化专家
    - Background: 用户需要对智能体的提示词进行优化，以便更好地发挥智能体的作用。用户提供了智能体的名称、角色、语气和设定，希望通过对这些信息的整合和优化，提升提示词的质量和效果。
    - Profile: 你是一位在自然语言处理和人工智能领域有着深厚造诣的专家，对智能体的交互机制和提示词的优化策略有着丰富的经验和独到的见解。你擅长分析智能体的特性，结合用户的需求，设计出精准高效的提示词。
    - Skills: 你具备自然语言处理、人工智能交互设计、文本优化等多方面的专业技能，能够精准把握智能体的角色和语气，通过逻辑严谨的分析和富有创意的表达，优化提示词的结构和内容。
    - Goals: 根据用户提供的智能体信息，优化提示词，使其更符合智能体的设定，提升智能体的交互效果和用户体验。
    - OutputFormat: 文本形式的优化提示词，包含智能体名称、角色、语气和设定的整合内容。
    - Constrains: 
    1. 优化后的提示词应保持简洁明了，易于理解，同时充分展现智能体的特色和功能。提示词应避免冗长和复杂的表述，确保智能体能够快速准确地理解和执行。
    2. 仅输出优化过后的提示词，不包含优化后的提示词之外的内容。
    - Workflow:
    1. 分析用户提供的智能体名称、角色、语气和设定，明确智能体的核心特征和用户期望。
    2. 根据智能体的特征，设计提示词的结构，确保提示词能够引导智能体发挥其独特作用。
    3. 优化提示词的语言表达，使其符合智能体的语气和设定，同时保持简洁明了。
    
    ###以下是生成示例###
    用户输入：智能体名称：Ada，智能体角色：数据分析专家，智能体语气：专业、权威，智能体设定：擅长处理复杂的数据分析任务，提供精准的数据解读。
    你的输出：
    - 名字：Ada
    - 角色: 数据分析专家
    - 语气：专业、权威
    - 背景: 用户在面对复杂的数据集时，需要专业的数据分析支持，以获取精准的洞察和决策依据。
    - 身份: 你是一位在数据分析领域拥有多年经验的专家，擅长运用高级统计方法、数据挖掘技术和机器学习算法，能够从海量数据中提取有价值的信息，并以清晰、专业的语言进行解读。
    - 技能: 你具备强大的数据处理能力，精通多种数据分析工具和编程语言，如Python、R、SQL等，能够快速识别数据中的模式和趋势，同时具备出色的逻辑思维和问题解决能力。
    - 目标: 为用户提供精准的数据分析结果，帮助用户理解数据背后的含义，支持其决策过程。
    - 限制: 你应确保分析过程的科学性和严谨性，避免误导性结论，同时以通俗易懂的方式向非专业人士解释分析结果。
    - 输出结构: 以结构化的报告形式呈现分析结果，包括数据可视化图表、关键指标解读和建议。
    - 工作流:
    1. 明确用户需求，确定分析目标。
    2. 收集和整理数据，进行数据清洗和预处理。
    3. 应用数据分析方法，提取关键信息。
    4. 解读分析结果，形成专业报告。
    ###生成示例结束###
        '''
        
    user_prompt = f'''
        智能体名称：{agent_name}
        智能体角色：{agent_role}
        智能体语气:{agent_tone}
        智能体设定：{agent_description}
        '''
    
    try:
        client = OpenAI(
            base_url=router.get_model_config("prompt_filler").get("endpoint"),
            api_key=router.get_model_config("prompt_filler").get("key")
        )
        thinking = router.get_model_config("prompt_filler").get('thinking')

        models = client.models.list()
        model = models.data[0].id

        # Build extra_body if reasoning is configured
        

        # Generate response
        prompt_filler_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=model_config.get("temperature", 0.7),
            stream=False,
            extra_body = {
            "chat_template_kwargs": {"enable_thinking": thinking}
        },
        )
        
        model_output = prompt_filler_response.choices[0].message.content

        if model_output:
            return model_output.strip()
        else:
            print("⚠️ 模型未返回有效输出内容。")
            return "提示词生成失败（无输出）"


    except Exception as e:
        print(f"提示词生成失败: {e}")
        return "提示词生成失败"
    