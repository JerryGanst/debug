from openai import OpenAI
from configs.load import load_config,ModelRouter

config = load_config()
router = ModelRouter(config)

def generate_page_abstract(input_text: str):
    prompt = f"""
        # 任务描述：
        你是一个高级文本摘要生成器，擅长精准提炼文本的关键信息。你的任务是根据提供的文本，生成**高质量的摘要**，该摘要将用于向量数据库检索。

        ## 生成要求：
        1. **摘要内容精准、浓缩，突出核心信息**：
           - **保留专业词汇**，如行业术语、专有名词、技术概念等，以确保摘要具有检索价值。
           - **保留关键表述**，例如时间、地点、人物、事件、规则、结论等重要信息。
           - **避免冗余和无关信息**，直接提炼**文本的核心内容**。

        2. **语言简洁，保持可读性**：
           - 不要使用“本文介绍了……”等无意义开头，**直接输出摘要内容**。
           - 句子结构清晰，**避免过度复杂的修饰**，但确保完整表达。
           - 适当使用逗号、顿号等标点，使摘要自然流畅。

        3. **摘要长度自适应**：
           - **推荐 200-400 字**，但不强制。如果原文较短，或关键信息有限，可适当缩短摘要，确保信息完整、精炼。
           - 如果原文内容丰富、信息密集，可适当延长摘要，但仍需保持简洁、去除冗余。

        4. **仅输出摘要文本**：
           - **不得** 解释任务要求，不得包含额外说明。
           - **不得** 生成标题，仅输出最终摘要。

        ---

        ## 示例：
        ### **示例输入**
        本文件之著作权及业务秘密内容属于立讯公司，非经准许不得翻印
        This document is the sole property of Luxshare. And should not be used in whole or in part without prior written permission.
        5.3 分离期
        5.3.1 员工在OA系统提交离职流程时，系统会自动弹出“保密协议”以提醒员工阅读并遵守协议，确认协议内容后，离职流程将进入下一步。
        5.4 实施与监督
        5.4.1 所有COC相关学习数据和考试结果将记录为个人档案的一部分，并作为试用期员工评估的一部分。如果员工未能通过COC考试或考试未完成，系统将限制其晋升和薪资调整。
        5.4.2 如果员工未能通过COC考试或考试未完成，当年的年度绩效将被评为C级或以下。
        5.4.3 现场HR负责向新员工提供COC协议以进行入职培训；同时，新员工必须签署“保密协议”和“诚信承诺”。此外，现场HR负责跟进并确保所有间接员工完成COC考试。
        5.4.4 HR中心负责每季度发布各单位的COC考试结果，并不定期审核政策和COC培训及考试。
        5.4.5 HR中心将指导各单位在一定期限内对未能执行政策的人员进行整改，并根据情况向责任人和责任主管提出相应的行政处罚。
        6. 附件
        6.1 “保密协议”
        6.2 “诚信承诺”

        ### **期望输出**
        立讯公司员工离职需确认“保密协议”，COC考试影响晋升、薪资及绩效考核。未完成考试者受限，HR 负责培训和考试监督，HR中心定期发布COC考试结果，监督政策执行，并可对违规人员进行整改或处罚。附件包含“保密协议”和“诚信承诺”。

        ---

        ## **待处理文本**
        请根据以下内容生成摘要：
        {input_text}
    """

    openai_api_base = router.get_model_config("page_abstract").get("endpoint")
    openai_api_key = router.get_model_config("page_abstract").get("key", "SOME_KEY")
    thinking = router.get_model_config("page_abstract").get("thinking")

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
        extra_body={
        "chat_template_kwargs": {"enable_thinking": thinking},
    },
    )
    page_abstract = response.choices[0].message.content.strip()
    return page_abstract


if __name__ == "__main__":
    t = generate_page_abstract(
        '''
        工离职单注：当前员工在线学习平台为i学堂OA-员工离职单OA-间接人员晋升申请单OA-员工薪资调整单系统名称：Quality Name  
        主题：Object  
        编号：AHR-001  
        管理系统：Management system  
        《全球商业行为与道德规范》  
        培训考核管理办法  
        版次：V2.0  
        页数：5 / 5  
        本文件之著作权及业务秘密内容属于立讯公司，非经准许不得翻印  
        This document is the sole property of Luxshare. And should not be used in whole or in part without prior written permission.  
        5. 作业内容  
        5.1 入职阶段  
        5.1.1 COC 课程为新员工入职培训必修课程，COC 考试结果为试用期考核必要项目，COC 考试不通过者视为试用不合格，不予正式转正。  
        5.1.2 新员工办理入职当日，厂区人资负责提供 COC 文件供新员工进行学习，同时与员工签订《保密保证书》、《廉洁保证书》，存档备案。  
        5.1.3 新员工本人须积极学习 COC 课程，于入职一个月内登陆员工在线学习平台完成 COC 课程学习，并通过 COC 考试。  
        5.2 在职阶段  
        5.2.1 每季度学习：每季度首月 1 日开始进行 COC 学习，间接员工须登陆员工在线学习平台参加巩固学习和考试，考试须在当季度内完成。  
        5.2.2 新员工入职当月的 COC 考试结果等同于当季度的学习与考试结果，当季度无需重复考试。
        '''
    )
    print(t)
