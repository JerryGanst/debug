import os
import sys
import subprocess


def check_unoconv():
    """确保 unoconv 已安装"""
    try:
        subprocess.run(["unoconv", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ unoconv 已安装")
    except FileNotFoundError:
        print("⚠️  unoconv 未安装，正在尝试安装...")
        subprocess.run(["sudo", "apt", "install", "-y", "unoconv"], check=True)
        print("✅ 安装完成")


def convert_doc_to_docx(doc_path):
    """转换单个 .doc 文件为 .docx"""
    docx_path = doc_path + "x"  # 直接在 .doc 后加 'x' 变成 .docx

    if os.path.exists(docx_path):
        print(f"✅ 已存在: {docx_path}，跳过转换")
    else:
        try:
            subprocess.run(["unoconv", "-f", "docx", doc_path], check=True)
            print(f"✅ 转换成功: {doc_path} → {docx_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 转换失败: {doc_path}, 错误: {e}")
            return

    # 删除原始 .doc 文件
    try:
        os.remove(doc_path)
        print(f"🗑️ 已删除原文件: {doc_path}")
    except Exception as e:
        print(f"⚠️ 无法删除 {doc_path}: {e}")


def batch_convert(directory):
    """转换目录下的所有 .doc 文件"""
    if not os.path.isdir(directory):
        print(f"❌ 错误: {directory} 不是有效目录")
        return

    for file_name in os.listdir(directory):
        if file_name.endswith(".doc") and not file_name.endswith(".docx"):  # 避免误删 .docx
            file_path = os.path.join(directory, file_name)
            convert_doc_to_docx(file_path)


def main():
    """主函数，接受参数"""
    if len(sys.argv) < 2:
        print("❌ 需要提供一个目录或文件路径作为参数")
        print("用法示例:")
        print("  python3 convert_doc_to_docx.py /path/to/directory")
        print("  python3 convert_doc_to_docx.py /path/to/file.doc")
        sys.exit(1)

    target_path = sys.argv[1]
    check_unoconv()  # 确保 unoconv 可用

    if os.path.isdir(target_path):
        batch_convert(target_path)
    elif os.path.isfile(target_path) and target_path.endswith(".doc"):
        convert_doc_to_docx(target_path)
    else:
        print(f"❌ 无效的路径: {target_path}")


if __name__ == "__main__":
    main()
