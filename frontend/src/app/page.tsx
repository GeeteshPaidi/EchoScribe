'use client';

import { useState } from 'react';

// Define the structure of the API response data
interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  speaker: string;
}

interface ApiResponse {
  summary: string;
  summary_audio_filename: string | null; // Changed from summary_audio_path
  diarized_transcript: TranscriptSegment[];
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!url || !url.includes('youtube.com')) {
      setError('Please enter a valid YouTube URL.');
      return;
    }

    // Reset state for new request
    setIsLoading(true);
    setResults(null);
    setError(null);

    try {
      // IMPORTANT: Use the full backend URL
      const response = await fetch('http://127.0.0.1:8000/process-video/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An API error occurred.');
      }

      const data: ApiResponse = await response.json();
      setResults(data);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-12 md:p-24 bg-gray-50 text-gray-800">
      <div className="z-10 w-full max-w-4xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl sm:text-5xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-teal-400 pb-4">
          EchoScribe 🎙️
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Transform YouTube videos into summaries, transcripts, and audio.
        </p>

        <div className="flex w-full items-center space-x-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="flex-grow p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="p-3 bg-blue-500 text-white rounded-lg shadow-sm hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? 'Processing...' : 'Process Video'}
          </button>
        </div>

        {isLoading && (
          <div className="text-center mt-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p className="mt-2">Processing video. This can take several minutes...</p>
          </div>
        )}

        {error && (
          <div className="mt-8 p-4 bg-red-100 text-red-700 border border-red-300 rounded-lg">
            <h3 className="font-bold">Error</h3>
            <p>{error}</p>
          </div>
        )}

        {results && (
          <div className="mt-12 w-full space-y-8">
            {/* Summary Section */}
            <section>
              <h2 className="text-2xl font-bold border-b pb-2 mb-4">Summary</h2>
              <div className="p-6 bg-white rounded-lg shadow">
                <p className="text-gray-700 leading-relaxed">{results.summary}</p>
                  {results.summary_audio_filename && (
                    <audio
                      controls
                      // The logic is now much cleaner
                      src={`http://127.0.0.1:8000/audio/${results.summary_audio_filename}`}
                      className="w-full mt-4"
                    >
                      Your browser does not support the audio element.
                    </audio>
                  )}
              </div>
            </section>

            {/* Transcript Section */}
            <section>
              <h2 className="text-2xl font-bold border-b pb-2 mb-4">Transcript</h2>
              <div className="p-6 bg-white rounded-lg shadow max-h-96 overflow-y-auto space-y-4">
                {results.diarized_transcript.map((segment, index) => (
                  <div key={index} className="flex flex-col sm:flex-row">
                    <p className="font-bold text-blue-600 w-32 mb-1 sm:mb-0">{segment.speaker}:</p>
                    <p className="flex-1">{segment.text}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </main>
  );
}