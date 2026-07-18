import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaRedo, FaTrash, FaCog } from 'react-icons/fa';

function VisualizerGlow({ state, level, isRecording }) {
  const color = state === 'Listening' ? '#22c55e' : state === 'Thinking' ? '#8b5cf6' : state === 'Speaking' ? '#06b6d4' : '#3b82f6';
  return (
    <div className="relative flex h-full w-full items-center justify-center overflow-hidden rounded-[1.5rem] border border-white/10 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_60%)]">
      <div className="absolute inset-0 rounded-full blur-3xl" style={{ background: `radial-gradient(circle, ${color}33 0%, transparent 70%)` }} />
      <motion.div
        animate={{ scale: state === 'Listening' ? [1, 1.06 + level * 0.2, 1] : state === 'Thinking' ? [1, 1.04, 1] : state === 'Speaking' ? [1, 1.08, 1] : 1 }}
        transition={{ duration: 0.9, repeat: Infinity, ease: 'easeInOut' }}
        className="relative flex h-56 w-56 items-center justify-center rounded-full border border-white/20"
        style={{ boxShadow: `0 0 70px ${color}40` }}
      >
        <div className="h-32 w-32 rounded-full border border-white/20" style={{ background: `radial-gradient(circle, ${color}99 0%, transparent 70%)` }} />
      </motion.div>
      <div className="absolute bottom-6 left-1/2 flex -translate-x-1/2 items-end gap-1">
        {Array.from({ length: 12 }).map((_, index) => (
          <motion.span
            key={index}
            animate={{ height: isRecording ? [10 + index % 3 * 6, 20 + (index % 4) * 8 + level * 40, 10 + index % 3 * 6] : [8, 12, 8] }}
            transition={{ duration: 0.6 + index * 0.04, repeat: Infinity, ease: 'easeInOut' }}
            className="w-1 rounded-full bg-white/70"
            style={{ height: 10 }}
          />
        ))}
      </div>
    </div>
  );
}

export default function Practice() {
  const [isRecording, setIsRecording] = useState(false);
  const [state, setState] = useState('Idle');
  const [transcript, setTranscript] = useState('Hello, I would like to improve my English speaking skills.');
  const [response, setResponse] = useState("That's wonderful! Tell me about your hobbies.");
  const [level, setLevel] = useState(0.3);

  useEffect(() => {
    if (!isRecording) return undefined;

    const interval = setInterval(() => {
      setLevel(Math.random() * 0.8 + 0.15);
    }, 140);
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleRecord = () => {
    if (isRecording) {
      setIsRecording(false);
      setState('Idle');
      return;
    }

    setIsRecording(true);
    setState('Listening');
    setTranscript('Listening to your voice...');

    window.setTimeout(() => {
      setState('Thinking');
      setTranscript('I love learning English.');
      setResponse('That sounds great! What motivates you to practice?');
    }, 1200);

    window.setTimeout(() => {
      setState('Speaking');
      setResponse('That sounds great! What motivates you to practice?');
    }, 2400);

    window.setTimeout(() => {
      setIsRecording(false);
      setState('Idle');
    }, 3600);
  };

  const stats = useMemo(() => [
    { label: 'Session Time', value: '04:12' },
    { label: 'Words Spoken', value: '38' },
    { label: 'Speaking Speed', value: '132 wpm' },
    { label: 'Fluency Score', value: '87%' },
  ], []);

  return (
    <div className="min-h-screen bg-background text-text">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <div className="text-lg font-semibold tracking-wide text-white">SpeakFlow</div>
        <div className="flex items-center gap-3">
          <button className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-zinc-300 transition hover:border-accent/40 hover:text-white">Settings</button>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accentSecondary text-sm font-semibold text-white">AI</div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl px-6 pb-12 lg:px-8">
        <section className="rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.05] to-white/[0.03] p-6 shadow-glow lg:p-8">
          <div className="flex flex-col gap-6 lg:flex-row">
            <div className="flex-1 rounded-[1.5rem] border border-white/10 bg-card/70 p-4">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.25em] text-accent">Visualizer</p>
                  <h2 className="text-xl font-semibold text-white">Speech Studio</h2>
                </div>
                <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-zinc-400">{state}</div>
              </div>
              <div className="relative h-[420px] overflow-hidden rounded-[1.5rem] border border-white/10">
                <VisualizerGlow state={state} level={level} isRecording={isRecording} />
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 rounded-full border border-white/10 bg-black/30 px-4 py-2 text-sm text-zinc-300">
                  {state === 'Idle' ? 'Click to Speak' : state === 'Listening' ? 'Listening...' : state === 'Thinking' ? 'Thinking...' : 'AI Speaking...'}
                </div>
              </div>
            </div>

            <div className="w-full max-w-sm rounded-[1.5rem] border border-white/10 bg-card/70 p-4">
              <div className="grid gap-3">
                {stats.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                    <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">{item.label}</p>
                    <p className="mt-2 text-lg font-semibold text-white">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <motion.article initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="rounded-[1.25rem] border border-white/10 bg-white/5 p-5">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">🎤 Your Speech</h3>
                <span className="text-sm text-zinc-400">Live</span>
              </div>
              <p className="max-h-36 overflow-auto whitespace-pre-wrap text-sm leading-7 text-zinc-300">{transcript}</p>
            </motion.article>
            <motion.article initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }} className="rounded-[1.25rem] border border-white/10 bg-white/5 p-5">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">🤖 AI Response</h3>
                <span className="text-sm text-zinc-400">AI</span>
              </div>
              <p className="max-h-36 overflow-auto whitespace-pre-wrap text-sm leading-7 text-zinc-300">{response}</p>
            </motion.article>
          </div>

          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <button onClick={handleRecord} className="rounded-full bg-gradient-to-r from-accent to-accentSecondary px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-accent/20 transition hover:scale-[1.02]">
              <span className="inline-flex items-center gap-2"><FaMicrophone /> {isRecording ? 'Listening' : 'Microphone'}</span>
            </button>
            <button className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-zinc-300 transition hover:border-white/20 hover:text-white"><span className="inline-flex items-center gap-2"><FaStop /> Stop</span></button>
            <button className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-zinc-300 transition hover:border-white/20 hover:text-white"><span className="inline-flex items-center gap-2"><FaRedo /> Replay</span></button>
            <button className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-zinc-300 transition hover:border-white/20 hover:text-white"><span className="inline-flex items-center gap-2"><FaTrash /> Clear</span></button>
            <button className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-zinc-300 transition hover:border-white/20 hover:text-white"><span className="inline-flex items-center gap-2"><FaCog /> Settings</span></button>
          </div>
        </section>
      </main>
    </div>
  );
}
