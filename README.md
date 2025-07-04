# RAG平台部署指南

## 1. 环境准备

### 1.1 模型存储位置
#### 测试环境 A100
```
/root/modelscope_models/
```

#### H20环境
```
/mnt/ai_data/models/huggingface_models/
```

#### L20环境
```
[请填写环境L20的模型位置]
```

### 1.2 配置文件位置
#### A100环境
```
/opt/rag-projects/rag-it/luxshare-ai-rag/vllm/
```

#### H20环境
```
/mnt/ai_data/models/
```

#### L20环境
```
[请填写环境L20的配置文件路径]
```

## 2. 模型部署

### 2.1 下载语言模型
以H20环境为例，从 https://huggingface.co/ 下载模型，解压到 `/mnt/ai_data/models/huggingface_models/` 目录下。

### 2.2 创建并激活虚拟环境
以H20环境为例：
```bash
cd /opt/venvs/vllm_for_models_venvs
python3.10 -m venv ./aaaa             # 在当前目录下创建名为aaaa的虚拟环境
source ./aaaa/bin/activate            # 激活该虚拟环境
```

### 2.3 安装依赖包
#### 安装vllm
```bash
pip install --upgrade pip
pip install uv
uv pip install vllm --torch-backend=auto
```

#### 安装flash infer
```bash
pip install flashinfer-python==0.2.2
```

### 2.4 创建模型配置文件
#### 2.4.1 创建配置文件
```bash
vim /mnt/ai_data/models/qwen3_32b_awq_32k_on_H20.yaml
```

#### 2.4.2 编辑配置参数
按 `i` 进入编辑模式，右键粘贴以下内容：

```yaml
host: "0.0.0.0"
port: 1002
uvicorn-log-level: "info"
served-model-name: "qwen3-32b-awq"
gpu_memory_utilization: 0.95
dtype: "bfloat16"
kv-cache-dtype: "fp8"
tensor-parallel-size: 4
pipeline-parallel-size: 1
```

#### 2.4.3 保存并退出
按 `ESC` 退出编辑模式，输入 `:wq` 保存并退出。

### 2.5 启动vLLM服务
以Qwen3 32B在H20*4环境为例：
```bash
export TORCH_CUDA_ARCH_LIST="9.0"

CUDA_VISIBLE_DEVICES=4,5,6,7 \
VLLM_ATTENTION_BACKEND=FLASHINFER \
vllm serve /mnt/ai_data/models/huggingface_models/Qwen_Qwen3-32B-AWQ \
  --config /mnt/ai_data/models/qwen3_32b_awq_32k_on_H20.yaml \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

## 3. RAG平台部署

### 3.1 下载RAG平台源码
前往公司GitLab，复制下载链接后使用git clone命令复制至指定位置。
例如在A100测试环境中：
```bash
git clone [repository_url] /opt/rag-projects/rag-it/luxshare-ai-rag
```

### 3.2 导航至项目目录
```bash
cd /opt/rag-projects/rag-it/luxshare-ai-rag
```

### 3.3 创建Python虚拟环境
```bash
python3.13 -m venv ./venv
```

### 3.4 激活虚拟环境
```bash
source ./venv/bin/activate
```

### 3.5 安装Python依赖包
```bash
pip install -r requirements.txt
```

### 3.6 配置agent_configs
#### 3.6.1 导航至configs文件夹
```bash
cd ./configs
```

#### 3.6.2 复制并修改配置文件
```bash
cp agent_configs_factory_it.yaml agent_configs.yaml
```
根据需要修改 `agent_configs.yaml` 文件中的配置参数。

### 3.7 启动RAG服务
在激活虚拟环境后，运行以下命令启动RAG平台：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9005
```

## 4. 服务验证

### 4.1 模型服务验证
如果vLLM模型服务启动成功，您将看到类似以下输出：
```
INFO:     Started server process [****]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4.2 RAG平台服务验证
如果RAG平台服务启动成功，您将看到类似以下输出：
```
INFO:     Started server process [****]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9005 (Press CTRL+C to quit)
```

## 5. 注意事项

1. 确保所有路径根据实际环境进行调整
2. 检查GPU显存是否足够支持模型运行
3. 确保网络连接正常，能够访问HuggingFace等外部资源
4. 定期检查日志文件以监控服务运行状态
