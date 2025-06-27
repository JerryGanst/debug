from openai import OpenAI


def commercial_api_answer(user_question, config: dict):
    openai_api_key = config.get("key")
    openai_api_base = config.get("endpoint")
    model = config.get("model")
    thinking = config.get("thinking")

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": user_question}],
        model=model,
        temperature=config.get("temperature"),
        extra_body={
            "chat_template_kwargs": {"enable_thinking": thinking},
        },
    )

    return response.choices[0].message.content
