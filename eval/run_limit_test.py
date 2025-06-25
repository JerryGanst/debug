import subprocess

# 定义 batch_size 和 time_interval 的取值范围
batchs = [1, 5, 10, 25, 50, 100]
intervals = [0, 3, 10, 30, 60]

# 运行 evaluation.py 并将输出保存到日志文件
for batch_size in [50]:
    for time_interval in intervals:
        if batch_size == 1 and time_interval > 0:
            continue
        log_filename = f"log_batch{batch_size}_interval{time_interval}.txt"
        command = ["python3", "evaluation.py", "./question1.json", "limit_test", str(batch_size), str(time_interval)]

        print(f"Running: {' '.join(command)} | Logging to {log_filename}")
       
        # 运行命令并将输出保存到日志文件
        with open(log_filename, "w") as log_file:
            subprocess.run(command, stdout=log_file, stderr=log_file, text=True)
