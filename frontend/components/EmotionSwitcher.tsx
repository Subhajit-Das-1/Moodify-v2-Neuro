"use client";

import { useState } from "react";
import CameraEmotion from "./CameraEmotion";
import VoiceEmotion from "./VoiceEmotion";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

type Mode = "camera" | "voice";

type Song = {
  name: string;
  artist: string;
  spotify_url: string;
  preview_url: string | null;
};

export default function EmotionSwitcher() {
  const [mode, setMode] = useState<Mode>("camera");
  const [emotion, setEmotion] = useState<string | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);

  // 🔥 THIS is the fix
  const onEmotionDetected = async (emotion: string) => {
    setEmotion(emotion);            // UI update ALWAYS
    setLoading(true);
    setSongs([]);

    try {
      const res = await fetch(
        `${BACKEND_URL}/recommend?emotion=${emotion}`
      );
      const data = await res.json();
      setSongs(data.songs ?? []);
    } catch (e) {
      console.error("Spotify fetch failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8">

      {/* MODE SWITCH */}
      <div className="flex justify-center gap-4">
        <button
          onClick={() => {
            setMode("camera");
            setEmotion(null);
            setSongs([]);
          }}
        >
          📷 Camera
        </button>

        <button
          onClick={() => {
            setMode("voice");
            setEmotion(null);
            setSongs([]);
          }}
        >
          🎤 Voice
        </button>
      </div>

      {/* INPUT */}
      {mode === "camera" ? (
        <CameraEmotion onResult={onEmotionDetected} />
      ) : (
        <VoiceEmotion onResult={onEmotionDetected} />
      )}

      {/* EMOTION */}
      {emotion && (
        <h2 className="text-3xl font-bold text-center capitalize">
          {emotion}
        </h2>
      )}

      {/* SONGS */}
      {loading && <p className="text-center">🎶 Loading songs…</p>}

      {songs.length > 0 && (
        <div className="grid md:grid-cols-2 gap-4">
          {songs.map((s, i) => (
            <div key={i} className="p-4 border rounded-xl">
              <p className="font-semibold">{s.name}</p>
              <p className="opacity-70">{s.artist}</p>
              <a
                href={s.spotify_url}
                target="_blank"
                className="text-green-400"
              >
                Open in Spotify
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
