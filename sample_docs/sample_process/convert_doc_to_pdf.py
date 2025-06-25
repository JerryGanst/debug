import subprocess
import os

from sample_docs.sample_process.utils import extract_text_from_pdf


def convert_to_pdf(input_path, output_folder="output_pdfs"):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")

    # Run LibreOffice with font embedding options
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf:writer_pdf_Export",
        "--outdir", output_folder, input_path
    ], check=True)

    print(f"Converted {input_path} to {output_path}")
    return output_path


if __name__ == "__main__":
    file_path = "/root/ns-rag/sample_docs/batch2_pdf/LXEP-026_1__防止歧视及骚扰作业程序.doc"  # Supports both .doc and .docx
    # pdf_path = convert_to_pdf(file_path)
    print(extract_text_from_pdf("/root/ns-rag/sample_docs/sample_process/output_pdfs/LXEP-026_1__防止歧视及骚扰作业程序.pdf"))
