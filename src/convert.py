import json
import os

template = """{{% extends "power-broker/_power-broker-summary-page.html" %}}
{{% block chapter %}}{chapter}{{% endblock %}}
{{% block index %}}{index}{{% endblock %}}
{{% block page %}}{page}{{% endblock %}}
{{% block content %}}
    {content}
{{% endblock %}}
"""

def convert_to_html(output_path):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../data/power-broker-metadata.json')
    chapter_data = json.load(open(filename, "r"))
    html_path = os.path.join(output_path, "html")
    if not os.path.exists(html_path):
        os.makedirs(html_path, exist_ok=True)

    for i, chapter in enumerate(chapter_data["chapters"][:-1]):
        chapter_filename = os.path.join(output_path, f"chapter_{i}_summary.txt")
        if not os.path.exists(chapter_filename):
            print(f"error: {chapter_filename} not found. Skipping")
            continue
        print(f"converting {chapter_filename}")
        summary = open(chapter_filename, "r").read()
        paragraphs = summary.split("\n\n")
        content = "\n\n".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
        html_page = template.format(
            chapter=chapter["name"],
            index=i,
            page=chapter["page"],
            content=content
        )
        html_num_dir = os.path.join(html_path, f'{i}')
        os.makedirs(html_num_dir, exist_ok=True)
        with open(os.path.join(html_num_dir, "index.html"), "w") as f:
            f.write(html_page)