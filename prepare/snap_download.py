import os

# os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from huggingface_hub import snapshot_download

if __name__ == "__main__":
    snapshot_download(
        repo_id="Qwen/QwQ-32B-AWQ",
        local_dir="/root/ns-rag/huggingface_models/Qwen_QwQ-32B-AWQ",
        # allow_patterns=["*Q8_0*"],  # For Q4_K_M
        # allow_patterns=["config.json", "params"],  # For Q4_K_M
        resume_download=True,  # 断点续传
        max_workers=8  # 并行下载加快速度
    )


# export HF_ENDPOINT='https://hf-mirror.com'