import sys
import os.path

from src.chapters import generate_chapter_files
from src.summary import generate_chapter_summaries
from src.convert import convert_to_html

output_path = "./output"
chapters_path = os.path.join(output_path, "chapters")

if len(sys.argv) < 2:
    exit(1)
cmd = sys.argv[1]

if cmd == "summary":
    generate_chapter_files(chapters_path)
    generate_chapter_summaries(chapters_path, "./output")

if cmd == "convert":
    convert_to_html(output_path)
