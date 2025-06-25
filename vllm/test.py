# SPDX-License-Identifier: Apache-2.0

from openai import OpenAI

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:6379/v1"
# openai_api_base = "http://172.16.10.2:6379/v1"

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

models = client.models.list()
model = models.data[0].id
print(f"Model: {model}")

if __name__ == "__main__":
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": "你是一个助手，帮我分解问题，解析为了回答这个问题，我需要收集哪些信息，而不是直接回答问题本身。"
        }, {
            "role": "user",
            "content": "SAP的工作流程"
        }],
        model=model,
    )

    print("Chat completion results:")
    print(chat_completion.choices[0].message.content)