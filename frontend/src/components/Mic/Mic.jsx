import React from "react";
import "./Mic.css";

function Mic({ onClick, isListening, audioLevel }) {
  const scale = 0.92 + audioLevel * 0.16;
  const glow = 0.4 + audioLevel * 0.35;

  return (
    <button
      className={`mic-button ${isListening ? "listening" : ""}`}
      onClick={onClick}
      type="button"
      aria-label={isListening ? "Stop listening" : "Start listening"}
    >
      <span
        className="mic-sphere"
        style={{
          transform: `scale(${scale})`,
          boxShadow: `0 0 ${Math.max(24, glow * 60)}px rgba(77, 166, 255, ${0.22 + glow * 0.25})`,
        }}
      >
        <span className="mic-icon"></span>
      </span>
    </button>
  );
}

export default Mic;