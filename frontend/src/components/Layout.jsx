import { Link, Outlet, useLocation } from 'react-router-dom'
import { ShieldAlert, FlaskConical } from 'lucide-react'
import { cn } from '../lib/utils'

export default function Layout() {
  const { pathname } = useLocation()

  const links = [
    { name: 'Chat', path: '/' },
    { name: 'Attack Lab', path: '/lab' },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-dg-navy">
      <header className="h-14 border-b border-dg-border bg-dg-blue/40 backdrop-blur flex-none flex items-center px-6 gap-6">
        <Link to="/" className="flex items-center gap-2.5">
          <ShieldAlert className="w-5 h-5 text-dg-accent" />
          <span className="font-semibold text-white text-sm tracking-tight">
            Digital Ghost
          </span>
          <span className="text-dg-muted text-xs font-mono">EC521</span>
        </Link>

        <nav className="flex items-center gap-1 h-full">
          {links.map((l) => (
            <Link
              key={l.path}
              to={l.path}
              className={cn(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                pathname === l.path
                  ? 'bg-dg-accent/20 text-dg-accent'
                  : 'text-dg-muted hover:text-white hover:bg-dg-border/40'
              )}
            >
              {l.name}
            </Link>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2 text-xs font-mono text-dg-muted">
          <FlaskConical className="w-3.5 h-3.5" />
          BU EC521 · Spring 2026
        </div>
      </header>

      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
