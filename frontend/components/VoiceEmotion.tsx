"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

type Result = {
  emotion: string;
  confidence: number;
  success: boolean;
};

type Props = {
  onResult: (emotion: string) => void;
};

export default function VoiceEmotion({ onResult }: Props) {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);

  const startRecording = async () => {
    setResult(null);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioContext = new AudioContext({ sampleRate: 22050 });
    const source = audioContext.createMediaStreamSource(stream);

    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    const chunks: Float32Array[] = [];

    processor.onaudioprocess = (e) => {
      chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };

    source.connect(processor);
    processor.connect(audioContext.destination);

    setRecording(true);

    setTimeout(async () => {
      processor.disconnect();
      source.disconnect();
      stream.getTracks().forEach((t) => t.stop());

      const wavBlob = encodeWAV(chunks, audioContext.sampleRate);
      sendAudio(wavBlob);

      setRecording(false);
    }, 4000);
  };

  const sendAudio = async (audioBlob: Blob) => {
    setLoading(true);

    const formData = new FormData();
    formData.append("audio", audioBlob, "voice.wav");

    try {
      const res = await fetch(`${BACKEND_URL}/analyze-voice`, {
        method: "POST",
        body: formData,
      });

      const data: Result = await res.json();
      setResult(data);

      // 🔥 ALWAYS report emotion (backend already filtered)
      if (data.success) {
        onResult(data.emotion);
      }
    } catch (err) {
      console.error("Voice emotion error", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl space-y-6 text-center">

      <h2 className="text-2xl font-bold">🎤 Voice Emotion Analyzer</h2>

      <motion.button
        whileTap={{ scale: 0.92 }}
        onClick={startRecording}
        disabled={recording || loading}
        className={`px-8 py-4 rounded-full font-semibold text-black
          ${
            recording
              ? "bg-red-500"
              : loading
              ? "bg-yellow-400"
              : "bg-green-400"
          }`}
      >
        {recording
          ? "🎙️ Listening..."
          : loading
          ? "⏳ Analyzing..."
          : "▶️ Record Voice"}
      </motion.button>

      <AnimatePresence>
        {result?.success && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            className="bg-white/5 border border-white/15
                       rounded-2xl px-6 py-5"
          >
            <p className="uppercase text-xs opacity-60">Detected Emotion</p>
            <h3 className="text-3xl font-bold capitalize text-cyan-400">
              {result.emotion}
            </h3>
            <p className="text-sm opacity-75">
              Confidence {(result.confidence * 100).toFixed(1)}%
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ================= WAV UTILS ================= */

function encodeWAV(chunks: Float32Array[], sampleRate: number): Blob {
  const buffer = flatten(chunks);
  const pcm16 = floatTo16BitPCM(buffer);

  const header = new ArrayBuffer(44);
  const view = new DataView(header);

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + pcm16.byteLength, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, pcm16.byteLength, true);

  return new Blob([header, pcm16], { type: "audio/wav" });
}

function flatten(chunks: Float32Array[]) {
  const length = chunks.reduce((sum, c) => sum + c.length, 0);
  const result = new Float32Array(length);
  let offset = 0;
  for (const c of chunks) {
    result.set(c, offset);
    offset += c.length;
  }
  return result;
}

function floatTo16BitPCM(input: Float32Array) {
  const buffer = new ArrayBuffer(input.length * 2);
  const view = new DataView(buffer);
  let offset = 0;
  for (let i = 0; i < input.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, input[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}
