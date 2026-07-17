import React from "react";
import "./styles/app.css";

import Background from "./components/Background/Background";
import Hero from "./components/Hero/Hero";

function App() {
  return (
    <div className="app">
      <Background />

      <div className="page-shell">
        <main className="main-container">
          <Hero />
        </main>
      </div>
    </div>
  );
}

export default App;