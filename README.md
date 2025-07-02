# 准备设置
## 0. 前置
### 0.1 模型位置
#### 测试环境 A100
/root/modelscope_models/
#### 正式环境 H20
[请填写正式环境H20的模型位置]

#### 环境 L20
[请填写环境L20的模型位置]


### 0.2 模型启动 configs.yaml 文件夹
#### 测试环境 A100
/opt/rag-projects/rag-it/luxshare-ai-rag/vllm/
#### 正式环境 H20
[请填写正式环境H20的configs.yaml文件夹路径]

### 环境 L20
[请填写环境L20的configs.yaml文件夹路径]

## 1. 启动模型
1.1 下载与解压语言模型
以A100为例，首先从https://huggingface.co/上面下载模型，解压在/root/modelscope_models下。

1.2 下载 RAG 平台源码并存放至指定位置
前往公司gitlab, 复制下载链接后使用git clone 复制至指定位置 如在 A100 中 /opt/rag-projects/rag-it/luxshare-ai-rag

1.3 创建虚拟环境

1.3.1 导航至项目目录中

```bash
cd /opt/rag-projects/rag-it/luxshare-ai-rag
```
1.3.2 创建虚拟环境  
```bash
python3.13 -m venv ./venv
```                      # 将3.10替换为实际需要的python版本
1.3.3 下载所需要用到的 python 包  
```bash
pip install -r "requirements.txt"
```
 补全 vllm 所需包    # 注：建议在别的地方安装vllm所需的虚拟环境，
```bash
  - pip install uv    # Windows时 当心360误删uv，提前把项目文件夹加入白名单
  - uv pip install vllm --torch-backend=auto
```
1.4 启动 vllm 服务
```bash
CUDA_VISIBLE_DEVICES=0 vllm serve /root/modelscope_models/Qwen_Qwen3-32B-FP8 \
  --config /opt/rag-projects/rag-it/luxshare-ai-rag/vllm/qwen3_32b_fp8_a100.yaml \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```
1.5 至此，若显示
INFO:     Started server process [581611]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
则模型正确启动

## 2. 启动 RAG 平台
2.1 激活虚拟环境
若根据步骤1.3正确创建了虚拟环境，此时项目目录下应有 .venv 文件夹
2.1.1 Linux
```bash
source .venv/bin/activate
```
2.1.2 Windows
```powershell
.\venv\Scripts\Activate.ps1
```

2.2 配置 agent_configs
导航至 configs 文件夹  
```bash
cd ./configs
```
复制并根据需要更改配置文件 
2.3 启动RAG服务
在激活虚拟环境后，运行以下命令启动RAG平台：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9005
``` 

2.4 验证服务启动
如果看到类似以下输出，则表示服务启动成功：
INFO:     Started server process [6976]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
