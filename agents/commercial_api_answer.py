from openai import OpenAI


def commercial_api_answer(user_question, config: dict):
    openai_api_key = config.get("key")
    openai_api_base = config.get("endpoint")
    model = config.get("model")

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": user_question}],
        model=model,
        temperature=config.get("temperature"),
    )

    return response.choices[0].message.content
