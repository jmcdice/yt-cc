#!/usr/bin/env python3

from yt_dlp import YoutubeDL
import re
import argparse
import os
import openai
import textwrap

# Get OpenAI API key from environment variable
openai.api_key = os.environ["OPENAI_API_KEY"]

# Define a variable to keep track of total tokens
total_tokens = 0

def download_youtube_subtitle(url):
    import io

    # Set YoutubeDL options
    ydl_opts = {
        'writesubtitles': True,    # Download subtitles
        'skip_download': True,     # Skip downloading the video
        'writeautomaticsub': True, # Write automatic subtitles
        'convertsubtitles': 'srt', # Convert the subtitles to srt format
        'subtitleslangs': ['en'],  # Download English subtitles only
        'outtmpl': 'output.srt'    # Name the subtitles file 'output.srt'
    }

    # Create a YoutubeDL instance with the specified options
    with YoutubeDL(ydl_opts) as ydl:
        # Download the subtitles and video information for the given URL
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', None)
        ydl.download([url])

    # Open the file containing the text
    with open("output.srt.en.vtt", "r") as f:
        text = f.read()

    # Remove the metadata and timecodes using regular expressions
    clean_text = re.sub(r"<.*?>", "", text)
    clean_text = re.sub(r".*align:start position:.*\n", "", clean_text)

    # Remove empty lines
    clean_text = "\n".join([line for line in clean_text.split("\n") if line.strip()])

    # Write the cleaned SRT text to a string buffer
    cleaned_srt = io.StringIO()
    for line in clean_text.split("\n"):
        cleaned_srt.write(line)
        cleaned_srt.write("\n")

    # Remove the temporary files
    os.remove("output.srt.en.vtt")

    # Return the title of the video and the cleaned SRT text
    return title, cleaned_srt.getvalue()

# Define function to break text into chunks
def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# Define function to summarize a chunk of text
def summarize_chunk(chunk, count):
    global total_tokens # Use the global total_tokens variable
    print(f"Sending request {count} to OpenAI API...")
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            { "role": "system", "content": "" },
            { "role": "user", "content": chunk },
        ],
        temperature=0.7,
    )
    summary = response['choices'][0]['message']['content']
    token_count = response['usage']['total_tokens']
    total_tokens += token_count # Update the total token count
    return summary.strip()

# Define function to rewrite a text using OpenAI
def rewrite_text(text):
    global total_tokens # Use the global total_tokens variable
    print("Sending rewrite request to OpenAI API...")
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
        messages=[
            { "role": "system", "content": "" },
            { "role": "user", "content": (
                    f"Please provide a brief summary of this video:\n{text}\n"), },
        ],
        temperature=0.7,
    )
    rewritten_text = response['choices'][0]['message']['content']
    token_count = response['usage']['total_tokens']
    total_tokens += token_count # Update the total token count
    return rewritten_text.strip()

# Define function to summarize a full text file
def summarize_file(text, chunk_size):
    global total_tokens # Use the global total_tokens variable
    # Clean up the text
    text = re.sub("\n+", "\n", text)
    text = re.sub("\n", ". ", text)
    text = re.sub(" +", " ", text)
    text = text.strip()

    # Break the text into chunks
    chunks = chunk_text(text, chunk_size)

    # Summarize each chunk
    summaries = []
    for i, chunk in enumerate(chunks):
        summary = summarize_chunk(chunk, i+1)
        summaries.append(summary)

    # Join the summaries together into a single text
    summary = " ".join(summaries)
    rewritten_summary = rewrite_text(summary)
    wrapped_summary = textwrap.fill(rewritten_summary, width=80)
    # Remove leading space in the content
    wrapped_summary = wrapped_summary.strip()
    return wrapped_summary

def get_openai_api_cost(num_tokens):
    cost_per_token = 0.00267
    total_cost = num_tokens * cost_per_token
    return total_cost


# Define main function
def main(chunk_size):
    global total_tokens # Use the global total_tokens variable
    # Download subtitles for the given video URL
    title, text = download_youtube_subtitle(args.url)
    summary = summarize_file(text, chunk_size)
    print("\n\nVideo Summary: ", title, "\n\n", summary, "\n\n")

    # Print the total token count
    total_cost = get_openai_api_cost(total_tokens)
    print(f"Total tokens used: {total_tokens} (Cost: {total_cost})\n\n")

# Parse command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument("--chunk_size", type=int, default=5000, help="size of each text chunk (default: 5000)")
    args = parser.parse_args()

    # Call the main function with the given arguments
    main(args.chunk_size)

       

