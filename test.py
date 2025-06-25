import requests

url = "http://127.0.0.1:10000/query"
# payload = {"user_id": "12345", "question": "我进入立讯后如何选择导师？"}
payload = {"user_id": "12345", "question": "内部讲师的选拔条件是什么？"}
# payload = {"user_id": "12345", "question": "求的专业技术知识题公司人力资源部在获得应聘资料后根据职位说明书等对应聘者进行初步筛选2对公司一线员等目检岗位视力含矫正"}
# payload = {"user_id": "12345", "question": "请假时间不到1天需要打卡嘛？"}
# payload = {"user_id": "12345", "question": "旷工会产生什么影响？"}
# payload = {"user_id": "12345", "question": "公司最新产品的生产工艺是什么？"}
# payload = {"user_id": "12345", "question": "LDP是什么"}
payload = {"user_id": "12345", "question": "LDP是什么？","model": "qwen-qwq-reasoning"}
# payload = {"user_id": "12345", "question": "怎么请假？","model": "qwen-qwq-reasoning"}


headers = {"Content-Type": "application/json"}

if __name__ == "__main__":
    response = requests.post(url, json=payload, headers=headers, stream=True)
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
    print(response)
