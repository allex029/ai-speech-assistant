# AI Speech Assistant

## Project Overview
AI Speech Assistant is a React + Vite frontend app that captures microphone input, displays a live transcript, and generates AI-corrected text output.

## Main Features
- Voice input through the microphone component
- Real-time transcript display
- AI-corrected text preview
- Theme toggle support
- Responsive full-screen hero layout

## Tech Stack
- React
- Vite
- CSS modules / component-level styles
- Web Speech API for speech recognition

## Project Structure
- frontend/src/App.jsx: app entry point
- frontend/src/components/Hero/Hero.jsx: main layout and voice interaction UI
- frontend/src/components/Mic/Mic.jsx: microphone button component
- frontend/src/context/ThemeContext.jsx: theme state management

## Notes
- The current UI is centered around a single-screen experience.
- The app is designed to be run locally with Vite.
