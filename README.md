# YouTube To Blog Post Converter

This application automatically converts YouTube videos into well-formatted blog posts by extracting video transcripts and transforming them using Google's Gemini 1.5 Pro AI model.

## Features

- **Automatic Transcript Extraction**: Retrieves transcripts directly from YouTube videos
- **AI-Powered Transformation**: Uses Google's Gemini 1.5 Pro to rewrite transcripts into engaging blog posts
- **Language Support**: Primary support for Portuguese with English fallback
- **Real-Time Streaming**: Watch the blog post being generated in real-time with progress indicators
- **User-Friendly Interface**: Simple web-based interface built with Gradio
- **Markdown Formatting**: Outputs blog posts with proper Markdown formatting
- **Error Handling**: Comprehensive error messages for various scenarios (missing transcripts, private videos, etc.)
- **Custom Writing Style**: Specify any blog URL as a reference for the AI to mimic that writing style

## Installation

1. Clone this repository:

git clone https://github.com/lcandido-tsc/youtube-blogger.git cd youtube-blogger

2. Install the required dependencies:

pip install -r requirements.txt

3. Create a `.env` file in the project root and add your Google API key:

GOOGLE_API_KEY=your_google_api_key_here

## Getting an API Key

To use this application, you'll need a Google API key with access to the Gemini models:

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create an account or sign in
3. Navigate to "API keys" and create a new key
4. Copy the key to your `.env` file

## Usage

1. Run the application:

python main.py

2. Access the web interface (Gradio will provide a local URL, typically http://127.0.0.1:7860)

3. Paste a YouTube URL into the text field and click "Gerar Post de Blog"

4. Watch as the application:
- Extracts the video transcript
- Generates a blog post in real-time
- Displays the final formatted blog post

## Requirements

- Python 3.8+
- langchain >= 0.1.0
- langchain-community >= 0.0.10
- langchain-google-genai >= 0.0.3
- youtube-transcript-api >= 0.6.1
- pytube >= 15.0.0
- python-dotenv >= 1.0.0
- gradio >= 4.0.0

## Limitations

- The YouTube video must have captions/subtitles enabled (either in Portuguese or English)
- Members-only videos and private videos cannot be processed
- The output follows a specific blog style format oriented toward health/educational content
- API usage may incur costs depending on your Google API plan

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using [LangChain](https://github.com/langchain-ai/langchain) for AI orchestration
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Interface created with [Gradio](https://www.gradio.app/)

