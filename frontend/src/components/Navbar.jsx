import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
      <Link to="/" className="text-lg font-semibold tracking-wide text-white">SpeakFlow</Link>
      <div className="flex items-center gap-3 text-sm text-zinc-400">
        <Link to="/" className="transition hover:text-white">Home</Link>
        <Link to="/practice" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-white transition hover:border-accent hover:bg-accent/10">Start Practicing</Link>
      </div>
    </nav>
  );
}
