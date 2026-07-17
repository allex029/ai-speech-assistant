import React from "react";
import "./Navbar.css";
import { FaMicrophone } from "react-icons/fa6";
import ThemeToggle from "../ThemeToggle/ThemeToggle";

function Navbar() {
  return (
    <header className="navbar">
      <div className="logo">
        <div className="logo-icon">
          <FaMicrophone />
        </div>

        <div className="logo-text">
          <h2>AI Speech Assistant</h2>
        </div>
      </div>

      <ThemeToggle />
    </header>
  );
}

export default Navbar;