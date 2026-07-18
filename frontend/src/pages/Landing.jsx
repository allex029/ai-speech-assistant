import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FaMicrophone, FaRobot, FaChartLine, FaVolumeUp } from 'react-icons/fa';

const features = [
  {
    icon: <FaMicrophone className="text-2xl text-accent" />, 
    title: 'Real-Time Speech Recognition',
    text: 'Whisper-powered transcription for instant text capture.',
  },
  {
    icon: <FaRobot className="text-2xl text-accent" />, 
    title: 'AI Conversation',
    text: 'Natural conversations powered by an LLM-style experience.',
  },
  {
    icon: <FaChartLine className="text-2xl text-accent" />,
    title: 'Fluency Analytics',
    text: 'Pause detection, speaking speed, filler words, and progress tracking.',
  },
  {
    icon: <FaVolumeUp className="text-2xl text-accent" />, 
    title: 'Voice Responses',
    text: 'AI replies with voice-ready responses in a premium experience.',
  },
];

const steps = ['User Speaks', 'Speech Transcribed', 'AI Understands', 'AI Responds', 'Voice Reply'];

export default function Landing() {
  return (
    <div className="min-h-screen bg-background text-text">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <div className="text-lg font-semibold tracking-wide text-white">SpeakFlow</div>
        <div className="hidden items-center gap-8 text-sm text-zinc-400 md:flex">
          <a href="#features" className="transition hover:text-white">Features</a>
          <a href="#about" className="transition hover:text-white">About</a>
          <Link to="/practice" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 font-medium text-white transition hover:border-accent hover:bg-accent/10">
            Start Practicing
          </Link>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-6 pb-20 lg:px-8">
        <section className="grid items-center gap-12 rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.03] px-8 py-16 shadow-glow md:px-12 lg:grid-cols-[1.1fr_0.9fr] lg:px-16 lg:py-24">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="mb-6 inline-flex rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-sm text-accent">
              AI English Speaking Coach
            </div>
            <h1 className="max-w-3xl text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
              Speak Better English with <span className="text-transparent bg-gradient-to-r from-accent to-accentSecondary bg-clip-text">AI</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-zinc-400">
              Practice natural conversations, receive detailed fluency feedback, and improve speaking confidence through a premium voice experience.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link to="/practice" className="rounded-full bg-gradient-to-r from-accent to-accentSecondary px-6 py-3 font-semibold text-white shadow-lg shadow-accent/20 transition hover:scale-[1.02]">
                Start Practicing
              </Link>
              <a href="#features" className="rounded-full border border-white/10 px-6 py-3 font-semibold text-zinc-300 transition hover:border-white/30 hover:text-white">
                Explore Features
              </a>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8 }} className="relative mx-auto flex h-[420px] w-full max-w-[480px] items-center justify-center">
            <div className="absolute inset-0 rounded-full bg-accent/15 blur-3xl" />
            <div className="absolute left-10 top-10 h-28 w-28 rounded-full bg-accent/20 blur-2xl" />
            <div className="absolute bottom-10 right-10 h-36 w-36 rounded-full bg-accentSecondary/20 blur-2xl" />
            <div className="relative flex h-72 w-72 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-accent/20 to-accentSecondary/10 shadow-[0_0_80px_rgba(59,130,246,0.2)]">
              <div className="h-40 w-40 rounded-full border border-white/20 bg-gradient-to-br from-accent/30 to-accentSecondary/40 animate-pulse" />
            </div>
          </motion.div>
        </section>

        <section id="features" className="mt-24">
          <div className="mb-8 text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-accent">Features</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">Everything you need to sound more natural</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {features.map((feature, index) => (
              <motion.article key={feature.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.08 }} className="rounded-2xl border border-white/10 bg-card/80 p-6 backdrop-blur">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-white/5">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-zinc-400">{feature.text}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section id="about" className="mt-24 rounded-[2rem] border border-white/10 bg-white/[0.03] p-8 lg:p-12">
          <div className="mb-10 text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-accent">How it Works</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">A simple path from speaking to feedback</h2>
          </div>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            {steps.map((step, index) => (
              <div key={step} className="flex items-center gap-3 rounded-full border border-white/10 bg-card/70 px-4 py-3 text-sm text-zinc-300">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-accent">{index + 1}</span>
                {step}
                {index < steps.length - 1 && <span className="ml-2 text-zinc-500">↓</span>}
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 px-6 py-8 text-sm text-zinc-500">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <p>© 2026 SpeakFlow</p>
          <div className="flex gap-6">
            <a href="#" className="transition hover:text-white">GitHub</a>
            <a href="#" className="transition hover:text-white">Privacy</a>
            <a href="#" className="transition hover:text-white">About</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
