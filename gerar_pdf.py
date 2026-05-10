import re
import glob
import subprocess
from pathlib import Path

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

output_pdf = "apresentacao_final.pdf"
temp_html = "_apresentacao_temp.html"


def natural_key(path):
    name = Path(path).stem
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", name)]


html_files = sorted(glob.glob("*.html"), key=natural_key)

if not html_files:
    raise FileNotFoundError("Nenhum arquivo .html encontrado na pasta.")

print("Ordem dos slides:")
for i, html in enumerate(html_files, start=1):
    print(f"{i:02d} - {html}")

pages = []

for html in html_files:
    abs_html = Path(html).resolve()
    file_url = "file:///" + str(abs_html).replace("\\", "/")

    pages.append(f"""
    <div class="page">
        <iframe src="{file_url}"></iframe>
    </div>
    """)

final_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">

<style>
@page {{
    size: 1280px 720px;
    margin: 0;
}}

html, body {{
    margin: 0;
    padding: 0;
    background: #0a0a0a;
}}

.page {{
    width: 1280px;
    height: 720px;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
}}

.page:last-child {{
    page-break-after: auto;
    break-after: auto;
}}

iframe {{
    width: 1280px;
    height: 720px;
    border: 0;
    display: block;
    overflow: hidden;
}}
</style>
</head>

<body>
{''.join(pages)}
</body>
</html>
"""

Path(temp_html).write_text(final_html, encoding="utf-8")

abs_temp = Path(temp_html).resolve()
abs_pdf = Path(output_pdf).resolve()

temp_url = "file:///" + str(abs_temp).replace("\\", "/")

subprocess.run([
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--allow-file-access-from-files",
    "--print-to-pdf-no-header",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=5000",
    f"--print-to-pdf={abs_pdf}",
    temp_url
], check=True)

Path(temp_html).unlink()

print(f"PDF final gerado: {output_pdf}")