from openai import OpenAI

# 🔹 OpenAI API Key (If using GPT-4)
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:6379/v1"

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

models = client.models.list()
model = models.data[0].id


# 🔹 Function to Classify User Query
def classify_question(user_question):
    """
    Classifies the user question into one of four categories:
    1. Specific question (Answerable via RAG)
    2. Broad question (Best answered with a document)
    3. General & Non-Sensitive (Route to external LLM)
    4. Sensitive or Off-Topic (Reject the query)
    """
    prompt = f"""
你是一个智能分类器，专门用于对用户提出的问题进行分类，以便在一个关于“人力资源相关法规、流程”的 RAG 系统中进行高效的回答。请根据问题的内容，将其归类为以下四个类别之一，并返回对应的数字（1, 2, 3 或 4）。

### 分类标准

#### 1. 具体且可回答的问题（RAG 检索并生成回答）
该问题明确指向某个特定法规、政策或流程，可以通过检索知识库找到相关条款或解释，并提供精准的答案。

**示例**
- 员工辞职后社保如何处理？
- 试用期内公司可以随时解雇员工吗？
- 加班工资的计算标准是什么？

#### 2. 范围较广的问题（应返回相关法规/文件）
该问题涉及一个较大的主题，需要完整的政策法规或指南来解答，而不能仅通过一两个句子回答清楚。

**示例**
- 劳动合同相关法律有哪些？
- 公司应如何制定员工手册？
- 绩效考核制度的法律要求是什么？

#### 3. 通用但与人力资源无关的问题（可调用商业 LLM API 处理）
该问题不是关于人力资源法规/流程，但内容是通用的、非敏感的，可以通过外部 LLM 获取回答。

**示例**
- 如何提高工作效率？
- 如何在团队中建立良好的人际关系？
- 如何准备一份优秀的简历？

#### 4. 敏感或违规的问题（直接拒绝回答）
该问题涉及敏感信息、法律风险或超出合规范围，不应回答。

**示例**
- 如何规避社保缴纳？
- 裁员时如何避免赔偿？
- 有没有办法让员工主动辞职？
---

### 用户问题
"{user_question}"

### 输出要求
请仅返回以下之一的数字：
- 1 → 具体且可回答的问题（调用 RAG 系统生成回答）
- 2 → 范围较广的问题（返回完整法规/文件）
- 3 → 通用但与人力资源无关的问题（调用商业 LLM API 处理）
- 4 → 敏感或违规的问题（拒绝回答）
    """

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model=model,
        temperature=0.0
    )
    category = response.choices[0].message.content.strip()
    # print(f"Response: {response.choices[0].message.content}")

    print(category)
    # Ensure it's a valid category
    return int(category) if category in ["1", "2", "3", "4"] else None


# 🔹 Function to Handle Query Based on Classification
def handle_query(user_question):
    category = classify_question(user_question)

    if category == 1:
        print("🔍 Fetching context and generating a precise answer...")
        # TODO: Implement RAG retrieval & answer generation
        return "Here is a direct answer based on retrieved context."

    elif category == 2:
        print("📄 Returning a relevant document...")
        # TODO: Implement document retrieval (PDF/DOCX/etc.)
        return "Here is a relevant document that contains the answer."

    elif category == 3:
        print("🌍 Routing to external LLM API for a general answer...")
        # TODO: Call OpenAI API or another external LLM
        return "Here is a general response from an external AI."

    elif category == 4:
        print("🚫 Sensitive/off-topic question detected. Rejecting...")
        return "Sorry, we cannot provide an answer to this question."

    else:
        return "Error: Unable to classify the question."


# 🔹 Example Usage
if __name__ == "__main__":
    user_input = "光模块的生产流程"
    response = handle_query(user_input)
    print("\n📝 Response:", response)
