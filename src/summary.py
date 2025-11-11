from openai import OpenAI
from .config import OPENAI_API_KEY
import semchunk
import tiktoken
import os

MAX_CHUNK_SIZE = 2048
MIN_CHUNK_SIZE = 16
COMPRESSION_FACTOR = 0.04

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def respond(self, system_prompt, user_prompt, temperature=0.2):
        response = self.client.responses.create(
            model="gpt-4.1",
            instructions=system_prompt,
            input=user_prompt,
            temperature=0.2,
        )
        return response.output_text

def get_chunks(text, encoding):
    chunker = semchunk.chunkerify('gpt-4', MAX_CHUNK_SIZE)
    chunks = chunker(text)
    chunks = [c for c in chunks if len(encoding.encode(c)) >= MIN_CHUNK_SIZE]
    return chunks

def get_tmp_dir(output_path, chapter_filename):
    chapter_name = os.path.basename(chapter_filename).split('.')[0]
    tmp_dir_name = os.path.join(output_path, f"tmp/{chapter_name}_summary_tmp")
    if not os.path.exists(tmp_dir_name):
        os.makedirs(tmp_dir_name)
    return tmp_dir_name

def load_existing_summaries(tmp_dir_name):
    summaries = []
    i = 0
    fullpath = lambda x: os.path.join(tmp_dir_name, f"summary_chunk_{x}.txt")
    while os.path.exists(fullpath(i)):
        with open(fullpath(i), "r") as f:
            summaries.append(f.read())
        i += 1
    return summaries

def summarize_chunks(client, chunks, encoding, tmp_dir_name):
    summaries = []
    for i, chunk in enumerate(chunks):
        chunk_size = len(encoding.encode(chunk))
        summary_token_count = int(chunk_size * COMPRESSION_FACTOR)
        print(f"Chunk {i} of ({len(chunks)-1}): {chunk_size} tokens")
        print(f"    Summary size: {summary_token_count} tokens")
        print(f"    Content: {repr(chunk[:60] + '...' if len(chunk) > 60 else chunk)}")
        
        prompt = get_prompt("single_excerpt_summary_prompt.txt")
        prompt = prompt.format(word_count=summary_token_count)
        print(f"    Prompt: {repr(prompt[:60] + '...' if len(prompt) > 60 else prompt)}")
        print()

        response = client.respond(
            system_prompt=prompt,
            user_prompt=chunk,
        )
        print(f"    Response: {response}")
        print()

        summaries.append(response)

        fullpath = os.path.join(tmp_dir_name, f"summary_chunk_{i}.txt")
        with open(fullpath, "w") as f:
            f.write(response)
    return summaries

def get_prompt(filename):
    dirname = os.path.dirname(__file__)
    prompt_path = os.path.join(dirname, "../prompts/", filename)
    return open(prompt_path, "r").read()

def merge_summaries(client, summaries, word_count):
    prompt = get_prompt("merge_summary_prompt.txt")
    prompt = prompt.format(word_count=word_count)
    print(f"Merge prompt: {repr(prompt[:60] + '...' if len(prompt) > 60 else prompt)}")

    return client.respond(
        system_prompt=prompt,
        user_prompt="\n\n".join(summaries),
    )

def style_summary(client, text):
    prompt = get_prompt("style_prompt.txt")
    print(f"Style prompt: {repr(prompt[:60] + '...' if len(prompt) > 60 else prompt)}")

    return client.respond(
        system_prompt=prompt,
        user_prompt=text,
    )

def save_final_summary(final_summary, output_path, chapter_filename):
    chapter_name = os.path.basename(chapter_filename).split('.')[0]
    fullpath = os.path.join(output_path, f"{chapter_name}_summary.txt")
    with open(fullpath, "w") as f:
        f.write(final_summary)

def summarize_chapter(client, output_path, chapter_filename):
    tmp_dir_name = get_tmp_dir(output_path, chapter_filename)
    chapter_text = open(chapter_filename, "r").read()
    encoding = tiktoken.encoding_for_model('gpt-4')
    chunks = get_chunks(chapter_text, encoding)

    print(f"Filename: {chapter_filename}")
    print(f"Number of tokens: {len(encoding.encode(chapter_text))}")
    print(f"Number of chunks: {len(chunks)}")
    print()

    summaries = []
    if os.path.exists(tmp_dir_name):
        summaries = load_existing_summaries(tmp_dir_name)

    if len(summaries) > 0:
        print(f"Found {len(summaries)} existing summaries in {tmp_dir_name}. Continuing from there.")
    else:
        summaries = summarize_chunks(client, chunks, encoding, tmp_dir_name)
    print()

    word_count = int(len(encoding.encode(chapter_text)) * COMPRESSION_FACTOR)
    merged_summary = merge_summaries(client, summaries, word_count)
    final_summary = style_summary(client, merged_summary)

    print(f"Final summary: {final_summary}")
    save_final_summary(final_summary, output_path, chapter_filename)

def generate_chapter_summaries(chapters_path, output_path):
    client = LLMClient()
    for i in range(52):
        chapter_filename = os.path.join(chapters_path, f"chapter_{i}.txt")
        if os.path.exists(chapter_filename):
            print(f"Processing {chapter_filename}...")
        summarize_chapter(client, output_path, chapter_filename)