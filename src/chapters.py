import json
import os

def write_chapters_to_files(metadata, full_text, output_folder):
    """
    Reads chapter, extracts chapters from a full text file,
    and writes each chapter to a separate file.

    Args:
      metadata: Object containing chapter metadata.
      full_text_file: Path to the text file containing the full text of the book.
    """

    os.makedirs(output_folder, exist_ok=True)

    for i, chapter in enumerate(metadata['chapters']):
        chapter_name = chapter['name']

        # Find the start index of the chapter
        start_index = full_text.find(chapter_name)
        if start_index == -1:
            print(f"Warning: Chapter '{chapter_name}' not found in the text.")
            continue

        # Find the start index of the next chapter (or end of file)
        try:
            next_chapter_name = metadata['chapters'][i + 1]['name']
            end_index = full_text.find(next_chapter_name)
        except IndexError:
            end_index = len(full_text)

        # Extract the chapter text
        chapter_text = full_text[start_index:end_index].strip()

        # Write the chapter to a separate file
        output_path = os.path.join(output_folder, f"chapter_{i}.txt")
        with open(output_path, 'w') as outfile:
            outfile.write(chapter_text)

def generate_chapter_files(output_path = None):
    curr_dir = os.path.dirname(__file__)

    metadata_file = os.path.join(curr_dir, '../data/power-broker-metadata.json')
    full_text_file = os.path.join(curr_dir, '../data/power-broker-full-text.txt')
    if output_path is None:
        output_path = os.path.join(curr_dir, './chapters')



    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    with open(full_text_file, 'r') as f:
        full_text = f.read()

    # remove the index
    full_text = full_text[full_text.find("THE POWER BROKER"):]

    write_chapters_to_files(metadata, full_text, output_path)
