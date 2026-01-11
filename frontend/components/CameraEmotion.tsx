"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

/* ✅ PROPS TYPE */
type CameraEmotionProps = {
  onResult: (emotion: string) => void;
};

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;

export default function CameraEmotion({ onResult }: CameraEmotionProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [emotion, setEmotion] = useState("neutral");
  const [confidence, setConfidence] = useState(0);

  const lastEmotionRef = useRef<string | null>(null);
  const requestLock = useRef(false);

  /* 🎥 Start camera */
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) videoRef.current.srcObject = stream;
    });
  }, []);

  /* 🔁 Capture loop */
  useEffect(() => {
    const id = setInterval(captureFrame, 1500);
    return () => clearInterval(id);
  }, []);

  const captureFrame = async () => {
    if (
      requestLock.current ||
      !videoRef.current ||
      !canvasRef.current
    ) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) return;

      requestLock.current = true;

      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");

      try {
        const res = await fetch(`${BACKEND_URL}/analyze-emotion`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json();

        if (!data?.emotion || data.confidence < 0.25) return;

        // ❌ ignore same emotion
        if (data.emotion === lastEmotionRef.current) return;

        lastEmotionRef.current = data.emotion;

        setEmotion(data.emotion);
        setConfidence(data.confidence);

        // 🔥 notify parent
        onResult(data.emotion);

      } catch (err) {
        console.error("Camera emotion error:", err);
      } finally {
        requestLock.current = false;
      }
    }, "image/jpeg");
  };

  return (
    <div className="space-y-8 text-center">

      {/* 🎥 Camera */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative mx-auto w-72"
      >
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="rounded-2xl border border-white/20
                     shadow-[0_0_80px_rgba(0,255,180,0.35)]"
        />
        <canvas ref={canvasRef} className="hidden" />
      </motion.div>

      {/* 🎭 Emotion Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={emotion}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          className="mx-auto max-w-xs
                     bg-white/5 backdrop-blur-xl
                     border border-white/15
                     rounded-2xl px-6 py-5"
        >
          <p className="uppercase text-xs tracking-widest opacity-60">
            Detected Emotion
          </p>

          <h2 className="text-3xl font-extrabold capitalize text-emerald-400">
            {emotion}
          </h2>

          <p className="mt-1 text-sm opacity-75">
            Confidence {(confidence * 100).toFixed(1)}%
          </p>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
