import os
os.environ['HF_ENDPOINT'] = "https://hf-mirror.com"
import json
from pathlib import Path
from huggingface_hub import snapshot_download

# 需要下载的模型列表
model_list = [
    # "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4",
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    # "Qwen/Qwen2.5-7B-Instruct",
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    # "Qwen/Qwen2.5-14B-Instruct",
    # "unsloth/DeepSeek-R1-Distill-Qwen-32B-bnb-4bit",
    # "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
    # "unsloth/DeepSeek-R1-Distill-Llama-70B-bnb-4bit",
    # "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/QwQ-32B-AWQ"
]

# 本地模型存放目录
MODEL_DIR = "./huggingface_models"

# 进度记录文件
PROGRESS_FILE = "download_progress.json"
progress_path = Path(PROGRESS_FILE)

# 读取已完成的下载列表
if progress_path.exists():
    with open(progress_path, "r") as f:
        downloaded_models = json.load(f)
else:
    downloaded_models = []

# 确保模型目录存在
os.makedirs(MODEL_DIR, exist_ok=True)


def download_model(model_name):
    """下载 Hugging Face 上的模型"""
    local_path = Path(MODEL_DIR) / model_name.replace("/", "_")

    # 如果模型已经下载过，跳过
    if model_name in downloaded_models:
        print(f"✅ 已下载: {model_name}，跳过...", flush=True)
        return

    print(f"🚀 开始下载: {model_name}...", flush=True)

    try:
        # 下载模型快照
        snapshot_download(
            repo_id=model_name,
            local_dir=local_path,
            resume_download=True,  # 断点续传
            local_dir_use_symlinks=False,  # 避免创建符号链接，确保完整下载
        )

        # 下载完成后，记录进度
        downloaded_models.append(model_name)
        with open(PROGRESS_FILE, "w") as f:
            json.dump(downloaded_models, f, indent=4)

        print(f"✅ 下载完成: {model_name}", flush=True)

    except Exception as e:
        print(f"❌ 下载失败: {model_name}，错误: {e}", flush=True)


# 逐个下载模型
for model in model_list:
    download_model(model)

print("🎉 所有模型下载完成！", flush=True)
