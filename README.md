# README for YouTube Subtitle Summarization
This Python script uses the yt_dlp library to download subtitles for a given YouTube video URL, cleans the text, and then summarizes it using the OpenAI API. The summarized text is then rewritten using OpenAI to make it more suitable for presenting as a news article.

## Requirements
- Python 3.x
- yt_dlp library (pip install yt_dlp)
- OpenAI API key

## Usage
- Clone the Git repository to your local machine.
- Install the required libraries with pip install yt_dlp.

Set your OpenAI API key as an environment variable: 
```
export OPENAI_API_KEY=your_api_key_here.
```

Run the script with the following command:
```console
  ./yt-video-summary.py "https://www.youtube.com/watch?v=5X1O5AS4nTc"
```

The script will download the subtitles for the YouTube video, summarize it using OpenAI, and print the summary to the console.

License
This script is licensed under the MIT License. See the LICENSE file for more information.
