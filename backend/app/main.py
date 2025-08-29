import os
import uuid
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import yt_dlp
from dotenv import load_dotenv
import soundfile as sf
import noisereduce as nr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import urllib.request
import zipfile
import numpy as np

# --- Our original, stable model imports ---
import whisper
from pyannote.audio import Pipeline
from transformers import pipeline as hf_pipeline
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

# --- Environment and Configuration ---
load_dotenv()
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)
HF_TOKEN = os.getenv("HF_TOKEN")
# --- THIS IS THE CRITICAL CHANGE FOR STABILITY ---
device = "cpu"
print(f"Forcing device to CPU for stability: {device}")

# --- Model Loading ---
print("Loading all AI models (this may take a moment on CPU)...")

whisper_model = whisper.load_model("base", device=device)
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)
diarization_pipeline = diarization_pipeline.to(torch.device(device))
summarizer = hf_pipeline("summarization", model="facebook/bart-large-cnn", device=-1) # -1 forces CPU for pipelines

# TTS Models
tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
tts_vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)

# TTS Speaker Embeddings
embeddings_dir = os.path.join(AUDIO_DIR, "cmu-arctic-xvectors")
embeddings_data_path = os.path.join(embeddings_dir, "spkrec-xvect")
if not os.path.exists(embeddings_data_path):
    os.makedirs(embeddings_dir, exist_ok=True)
    zip_path = os.path.join(embeddings_dir, "spkrec-xvect.zip")
    urllib.request.urlretrieve("https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors/resolve/main/spkrec-xvect.zip", zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(embeddings_dir)
    os.remove(zip_path)

all_xvectors = [torch.tensor(np.load(os.path.join(embeddings_data_path, f))) for f in sorted(os.listdir(embeddings_data_path)) if f.endswith('.npy')]
speaker_embeddings_tensor = torch.stack(all_xvectors).to(device)
speaker_embeddings = speaker_embeddings_tensor[7306].unsqueeze(0)

print("All models loaded successfully.")

# --- Pydantic Models ---
class URLModel(BaseModel):
    url: HttpUrl

# --- FastAPI App & CORS ---
app = FastAPI(title="EchoScribe API")
origins = ["http://localhost:3000", "http://localhost"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/process-video/")
async def process_video(payload: URLModel):
    youtube_url = str(payload.url)
    unique_id = uuid.uuid4()
    original_wav_path = os.path.join(AUDIO_DIR, f"{unique_id}_original.wav")

    # 1. Download and Noise Reduction
    try:
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': original_wav_path.replace('.wav', ''), 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([youtube_url])
        audio_data, sample_rate = sf.read(original_wav_path)
        if audio_data.ndim > 1: audio_data = audio_data.mean(axis=1)
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)
        cleaned_wav_path = os.path.join(AUDIO_DIR, f"{unique_id}_cleaned.wav")
        sf.write(cleaned_wav_path, reduced_noise_audio, sample_rate)
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error during audio prep: {str(e)}")

    # 2. Transcription
    transcription_result = whisper_model.transcribe(cleaned_wav_path)
    
    # 3. Diarization
    diarization_result = diarization_pipeline(cleaned_wav_path, min_speakers=2, max_speakers=7)

    # 4. Merging and Formatting
    final_transcript = []
    full_transcript_text = ""
    for segment in transcription_result['segments']:
        start, end, text = segment['start'], segment['end'], segment['text']
        center = start + (end - start) / 2
        speaker = "UNKNOWN"
        for turn, _, label in diarization_result.itertracks(yield_label=True):
            if turn.start <= center <= turn.end:
                speaker = label
                break
        final_transcript.append({"speaker": speaker, "text": text, "start": start, "end": end})
        full_transcript_text += f"{speaker}: {text.strip()} "

    # 5. Summarization
    summary = ""
    if full_transcript_text:
        summary_result = summarizer(full_transcript_text, max_length=250, min_length=50, do_sample=False)
        summary = summary_result[0]['summary_text']
    
    # 6. Text-to-Speech
    summary_audio_filename = None
    if summary:
        try:
            summary_audio_path = os.path.join(AUDIO_DIR, f"{unique_id}_summary.wav")
            inputs = tts_processor(text=summary, return_tensors="pt").to(device)
            speech = tts_model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=tts_vocoder)
            sf.write(summary_audio_path, speech.cpu().numpy(), samplerate=16000)
            summary_audio_filename = os.path.basename(summary_audio_path)
        except Exception as e:
            print(f"TTS generation failed: {e}")

    return {
        "message": "Processing completed successfully.",
        "summary": summary,
        "summary_audio_filename": summary_audio_filename,
        "diarized_transcript": final_transcript,
    }

app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")