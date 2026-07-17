import React from "react";
import "./ThemeToggle.css";
import { useTheme } from "../../context/ThemeContext";

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className={`theme-btn ${theme}`}
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      type="button"
    >
      <span className="toggle-circle">
        {theme === "dark" ? "🌙" : "☀️"}
      </span>
    </button>
  );
}

export default ThemeToggle;