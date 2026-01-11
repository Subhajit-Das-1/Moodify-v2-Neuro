import EmotionSwitcher from "@/components/EmotionSwitcher";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-10">
      <h1 className="text-4xl font-extrabold">🎧 Moodify-v2-Neuro</h1>
      <p className="opacity-80 max-w-xl text-center">
        Choose how you want your emotion detected — face or voice —
        and get music recommendations accordingly.
      </p>

      <EmotionSwitcher />
    </main>
  );
}
