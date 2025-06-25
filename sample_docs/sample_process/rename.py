import os
import re

# 设置你的文件夹路径
folder_path = "../batch2"

# 定义不兼容字符的正则表达式
invalid_chars_pattern = r"[ \(\)【】《》“”‘’\[\]{}<>!@#$%^&*+=|\\/,]"


def sanitize_filename(filename):
    """
    处理文件名：
    1. 替换空格和其他特殊字符为下划线或删除
    2. 确保文件扩展名保留
    """
    name, ext = os.path.splitext(filename)  # 分离文件名和扩展名
    sanitized_name = re.sub(invalid_chars_pattern, "_", name)  # 替换不兼容字符
    return sanitized_name + ext


if __name__ == "__main__":
    # 遍历文件夹
    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        if os.path.isfile(old_path):  # 仅处理文件，跳过文件夹
            new_filename = sanitize_filename(filename)
            print("try process one file, no need to change")
            new_path = os.path.join(folder_path, new_filename)

            if old_path != new_path:  # 避免无意义的重命名
                try:
                    os.rename(old_path, new_path)
                    print(f"重命名: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"重命名失败: {filename}，错误: {e}")
