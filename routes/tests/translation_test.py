import requests
import json

# API 地址
API_URL = "http://localhost:10000/translate"

# 支持的语言列表
SUPPORTED_LANGUAGES = ["中文", "英文", "越南语", "西班牙语"]

# 不支持的语言列表
UNSUPPORTED_LANGUAGES = ["法语", "德语", "日语"]

# 测试用户 ID 和源文本
USER_ID = "test_user"
SOURCE_TEXT = "我已在文档中增加了 target_language 必须严格匹配支持的语言的提醒，并强调如果不匹配则请求将失败。如果需要进一步优化，请告诉我！"


# 打印响应详情的函数
def print_response(response):
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print("-" * 50)


if __name__ == "__main__":
    # 测试支持的语言
    print("测试支持的语言...")
    for lang in SUPPORTED_LANGUAGES:
        payload = {
            "user_id": USER_ID,
            "target_language": lang,
            "source_text": SOURCE_TEXT
        }
        response = requests.post(API_URL, json=payload)
        print(f"请求目标语言: {lang}")
        print_response(response)
        # 验证响应
        if response.status_code == 200:
            data = response.json()
            if "translation_result" in data:
                print(f"{lang} 翻译成功")
            else:
                print(f"{lang} 返回了意外的响应")
        else:
            print(f"{lang} 返回了意外的状态码: {response.status_code}")

    # 测试不支持的语言
    # print("测试不支持的语言...")
    # for lang in UNSUPPORTED_LANGUAGES:
    #     payload = {
    #         "user_id": USER_ID,
    #         "target_language": lang,
    #         "source_text": SOURCE_TEXT
    #     }
    #     response = requests.post(API_URL, json=payload)
    #     print(f"请求目标语言: {lang}")
    #     print_response(response)
    #     # 验证响应
    #     if response.status_code == 400:
    #         data = response.json()
    #         if "error" in data:
    #             print(f"正确拒绝了不支持的语言: {lang}")
    #         else:
    #             print(f"{lang} 返回了意外的响应")
    #     else:
    #         print(f"{lang} 返回了意外的状态码: {response.status_code}")
