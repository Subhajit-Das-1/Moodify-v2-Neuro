"use client";

import { motion } from "framer-motion";

type Song = {
  name: string;
  artist: string;
  spotify_url: string;
  preview_url: string | null;
};

export default function SongGrid({
  emotion,
  songs,
}: {
  emotion: string;
  songs: Song[];
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* 🎧 Header */}
      <div className="text-center space-y-1">
        <p className="uppercase text-xs tracking-widest opacity-60">
          Music for your mood
        </p>
        <h3 className="text-3xl font-extrabold capitalize text-emerald-400">
          {emotion}
        </h3>
      </div>

      {/* 🎵 Songs */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {songs.map((song, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.04 }}
            transition={{ type: "spring", stiffness: 300 }}
            className="rounded-2xl bg-white/5 backdrop-blur-xl
                       border border-white/10 p-5
                       hover:border-emerald-400/40"
          >
            <div className="space-y-2">
              <h4 className="font-bold text-lg">{song.name}</h4>
              <p className="text-sm opacity-70">{song.artist}</p>
            </div>

            <a
              href={song.spotify_url}
              target="_blank"
              className="inline-block mt-4 text-sm font-semibold
                         text-emerald-400 hover:underline"
            >
              ▶ Open in Spotify
            </a>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}
