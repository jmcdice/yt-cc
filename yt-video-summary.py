#!/usr/local/bin/python3

from yt_dlp import YoutubeDL
import re
import argparse
import os
import openai
import textwrap

# Get OpenAI API key from environment variable
openai.api_key = os.environ["OPENAI_API_KEY"]

def download_youtube_subtitle(url):
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

    # Write the cleaned SRT text to a new file
    with open('output_cleaned.srt', 'w') as f:
        f.write(clean_text)

    with open('output_cleaned.srt', 'r') as input_file, open('final.srt', 'w') as output_file:
        unique_lines = set()
        for line in input_file:
            if line.strip() not in unique_lines:
                unique_lines.add(line.strip())
                output_file.write(line)

    # Remove the temporary files
    os.remove("output.srt.en.vtt")
    os.remove("output_cleaned.srt")
    
    # Return the title of the video and the cleaned SRT text
    return title, clean_text

# Define function to break text into chunks
def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# Define function to summarize a chunk of text
def summarize_chunk(chunk, count):
    print(f"Sending request {count} to OpenAI API...")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=chunk,
        temperature=0.7,
        max_tokens=400,
        n=1,
        stop=None,
    )
    summary = response.choices[0].text
    return summary.strip()

# Define function to rewrite a text using OpenAI
def rewrite_text(text):
    print("Sending rewrite request to OpenAI API...")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Please provide a long and detailed summary of this video as if we were presenting a news article, in conversational language:\n{text}\n",
        temperature=0.7,
        max_tokens=400,
        n=1,
        stop=None,
    )
    rewritten_text = response.choices[0].text
    return rewritten_text.strip()

# Define function to summarize a full text file
def summarize_file(text, chunk_size):
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
    return wrapped_summary

# Define main function
def main(chunk_size):
    # Download subtitles for the given video URL
    title, text = download_youtube_subtitle(args.url)
    summary = summarize_file(text, chunk_size)
    print("\n\nVideo Summary: ", title, "\n\n", summary, "\n\n")


# Parse command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument("--chunk_size", type=int, default=5000, help="size of each text chunk (default: 5000)")
    args = parser.parse_args()

    # Call the main function with the given arguments
    main(args.chunk_size)

