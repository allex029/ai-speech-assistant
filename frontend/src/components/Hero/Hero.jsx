import React, { useEffect, useRef, useState } from "react";
import "./Hero.css";
import Mic from "../Mic/Mic";
import ThemeToggle from "../ThemeToggle/ThemeToggle";

function Hero() {
  const [rawText, setRawText] = useState(
    "Tap the sphere to start listening. Your spoken words will appear here."
  );
  const [correctedText, setCorrectedText] = useState(
    "AI-corrected text will appear here once speech begins."
  );
  const [isListening, setIsListening] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0.24);
  const [statusText, setStatusText] = useState("Ready to listen");
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);

  const cleanupAudio = () => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      cleanupAudio();
    };
  }, []);

  const formatCorrection = (value) => {
    if (!value) return "AI-corrected text will appear here once speech begins.";

    return value
      .trim()
      .replace(/\s+/g, " ")
      .replace(/(^|\.\s+)([a-z])/g, (match, prefix, letter) => `${prefix}${letter.toUpperCase()}`)
      .replace(/\s+([,.;:!?])/g, "$1");
  };

  const startListening = async () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setStatusText("Listening paused");
      cleanupAudio();
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatusText("Speech recognition is not available in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
      setIsListening(true);
      setStatusText("Listening...");
      setRawText("Listening for your voice...");
    };

    recognition.onresult = (event) => {
      let interim = "";
      let finalText = "";

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += `${result} `;
        } else {
          interim += `${result} `;
        }
      }

      const combined = `${finalText}${interim}`.trim();
      setRawText(combined || "Listening for your voice...");
      setCorrectedText(formatCorrection(combined));
    };

    recognition.onerror = () => {
      setStatusText("Microphone access is unavailable right now.");
      cleanupAudio();
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setStatusText("Listening ended");
      cleanupAudio();
    };

    recognitionRef.current = recognition;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateAudio = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length / 255;
        setAudioLevel(0.2 + average * 0.95);
        rafRef.current = requestAnimationFrame(updateAudio);
      };

      updateAudio();
      recognition.start();
    } catch (error) {
      setStatusText("Allow microphone access to begin listening.");
      setIsListening(false);
      cleanupAudio();
    }
  };

  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-topbar">
          <span className="hero-badge">AI Voice Studio</span>
          <ThemeToggle />
        </div>

        <h1>
          Speak naturally.
          <br />
          <span>We turn it into polished text.</span>
        </h1>

        <p>
          Capture your voice, review the raw transcript on the left, and let the AI refine the message on the right.
        </p>

        <div className="mic-shell">
          <Mic onClick={startListening} isListening={isListening} audioLevel={audioLevel} />
        </div>

        <div className="status-pill">{statusText}</div>

        <div className="workspace-grid">
          <article className="transcript-panel">
            <div className="panel-label">Raw transcript</div>
            <p className="panel-text">{rawText}</p>
          </article>

          <article className="transcript-panel ai-panel">
            <div className="panel-label">AI corrected text</div>
            <p className="panel-text">{correctedText}</p>
          </article>
        </div>
      </div>
    </section>
  );
}

export default Hero;