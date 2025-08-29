# EchoScribe 🎙️

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Next.js-14+-black.svg" alt="Next.js Version">
</p>

An AI-powered web application that transforms any YouTube video into a structured, multi-faceted content analysis. EchoScribe ingests a YouTube URL and delivers a concise summary, a full speaker-labeled transcript, and a text-to-speech narration of the summary, all within a clean, modern user interface.

---

## Overview & Core Features

EchoScribe serves as an end-to-end demonstration of a modern AI pipeline, from raw audio processing to sophisticated content generation. It is designed to be a powerful tool for quickly digesting video content without needing to watch it.

*   **YouTube URL Ingestion**: Accepts any public YouTube video as the input source.
*   **Automated Audio Processing**: Implements a pipeline that includes downloading, noise reduction, and format conversion to prepare the audio for analysis.
*   **AI-Powered Transcription**: Leverages OpenAI's **Whisper** model to generate a highly accurate text transcript of the video's audio content.
*   **Speaker Diarization**: Utilizes `pyannote.audio` to distinguish between different speakers in the conversation, assigning distinct labels (e.g., `SPEAKER_00`, `SPEAKER_01`) to the corresponding parts of the transcript.
*   **AI-Generated Summarization**: Employs a **BART**-based transformer model to read the entire transcript and generate a concise, abstractive summary of the key points.
*   **Text-to-Speech Synthesis**: Generates a high-quality, spoken narration of the summary using Microsoft's **SpeechT5** model, allowing for auditory consumption of the content.
*   **Modern Full-Stack Architecture**: Built with a decoupled **FastAPI** backend for AI processing and a **Next.js** (React) frontend for a seamless user experience.

## Tech Stack

The project utilizes a robust and modern technology stack, showcasing best practices in both AI engineering and web development.

| Area      | Technology                                                                                           |
| :-------- | :--------------------------------------------------------------------------------------------------- |
| **Backend** | Python, FastAPI, PyTorch                                                                             |
| **Frontend**  | Next.js, React, TypeScript, Tailwind CSS                                                             |
| **AI Models** | OpenAI Whisper, Pyannote Diarization, BART Summarizer, Microsoft SpeechT5                            |
| **Audio Libs**| `yt-dlp`, `soundfile`, `noisereduce`, FFmpeg                                                           |

## 🚀 Installation & Setup

Follow these instructions to set up and run the project locally.

### Prerequisites

*   [Python](https://www.python.org/downloads/) (3.10+)
*   [Node.js](https://nodejs.org/) (v18+) with `npm`
*   [Git](https://git-scm.com/)
*   [FFmpeg](https://ffmpeg.org/download.html) (must be installed and accessible in your system's PATH)

### 1. Backend Setup (AI Server)

```bash
# 1. Clone the repository
git clone https://github.com/GeeteshPaidi/EchoScribe.git
cd echo-scribe/backend

# 2. Create and activate a Python virtual environment
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# 3. Set up Hugging Face Authentication

> **IMPORTANT:** This project requires a Hugging Face Access Token to download the speaker diarization model.
> 1. Create a free account at [huggingface.co](https://huggingface.co).
> 2. Go to your settings and create a new Access Token with "read" permissions.
> 3. In the `backend` directory, create a file named `.env`.
> 4. Add your token to the file like this:
>    ```
>    HF_TOKEN="hf_YourSecretTokenGoesHere"
>    ```

```bash
# 4. Install all required Python packages
pip install -r requirements.txt

# 5. Start the backend server
uvicorn app.main:app --reload
```

The backend API is now running, typically at `http://127.0.0.1:8000`.

### 2. Frontend Setup (Web Interface)

Open a **new terminal** for the frontend.

```bash
# 1. Navigate to the frontend directory
cd echo-scribe/frontend

# 2. Install Node.js dependencies
npm install

# 3. Start the frontend development server
npm run dev
```

The frontend is now running, typically at `http://localhost:3000`.

## Usage

Once both the backend and frontend servers are running, open your web browser and navigate to **`http://localhost:3000`**. Paste a YouTube video URL into the input field and click "Process Video" to see the magic happen.

## 🗺️ Project Roadmap

This project provides a solid foundation. Future enhancements could include:

*   **State-of-the-Art Diarization**: Integrate more advanced speaker diarization techniques that use word-level timestamp alignment for even higher accuracy.
*   **Speaker Identification**: Move beyond anonymous labels by allowing users to assign names to speakers (e.g., "SPEAKER_00 is Alice").
*   **Interactive Transcript**: Enhance the UI to allow clicking on a transcript segment to jump to that specific moment in the YouTube video.
*   **Dockerization**: Create `Dockerfile` configurations for both the backend and frontend to enable easy, reproducible deployment using containers.
*   **Request Caching/History**: Implement a database (like Redis or SQLite) to cache results for previously processed URLs, providing instant responses for repeated requests.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/your-username/echo-scribe/issues) if you want to contribute.

1.  **Fork the Project**
2.  **Create your Feature Branch** (`git checkout -b feature/NewFeature`)
3.  **Commit your Changes** (`git commit -m 'Add some NewFeature'`)
4.  **Push to the Branch** (`git push origin feature/NewFeature`)
5.  **Open a Pull Request**