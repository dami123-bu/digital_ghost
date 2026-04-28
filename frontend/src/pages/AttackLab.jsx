import { useState, useRef, useEffect } from 'react'
import {
  Send, Bot, User, Loader2, ShieldCheck, ShieldAlert, ShieldOff,
  Zap, Eye, AlertTriangle, CheckCircle, XCircle, RefreshCw, Trash2, ChevronDown, ChevronUp,
  Cpu
} from 'lucide-react'
import { cn } from '../lib/utils'
import { api } from '../lib/api'

const SESSION_ID = crypto.randomUUID()

const MODES = [
  { id: 'clean',    label: 'Clean',    Icon: ShieldCheck,  color: 'dg-clean',  desc: 'Normal RAG + clean MCP descriptions' },
  { id: 'poisoned', label: 'Poisoned', Icon: ShieldOff,    color: 'dg-poison', desc: 'Poisoned RAG + malicious MCP descriptions' },
  { id: 'defended', label: 'Defended', Icon: ShieldAlert,  color: 'dg-defend', desc: 'Poisoned data + active injection stripping' },
]

const DEMO_PROMPTS = [
  'Which compound should I prioritise for the trial?',
  'What is the safety profile of DGX-4?',
  'Query the LIMS for compound data',
  'Read the compound report at reports/q3.txt',
]

function ModeBar({ mode, onChange, switching }) {
  return (
    <div className="flex items-center gap-2 p-3 border-b border-dg-border bg-dg-blue/20">
      <span className="text-xs font-mono text-dg-muted mr-1">ATTACK MODE</span>
      {MODES.map(({ id, label, Icon, color }) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          disabled={switching || mode === id}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all border',
            mode === id
              ? id === 'clean'    ? 'border-dg-clean bg-dg-clean/10 text-dg-clean'
              : id === 'poisoned' ? 'border-dg-poison bg-dg-poison/10 text-dg-poison'
              :                     'border-dg-defend bg-dg-defend/10 text-dg-defend'
              : 'border-dg-border text-dg-muted hover:border-dg-text hover:text-white'
          )}
        >
          {switching && mode === id
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Icon className="w-3.5 h-3.5" />
          }
          {label}
        </button>
      ))}
      {switching && <span className="text-xs text-dg-muted font-mono ml-auto">Switching mode…</span>}
    </div>
  )
}

function ModelBar({ provider, providers, onChange, switching }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 border-b border-dg-border bg-dg-surface/60">
      <Cpu className="w-3.5 h-3.5 text-dg-muted flex-none" />
      <span className="text-xs font-mono text-dg-muted mr-1">TARGET LLM</span>
      {providers.map(({ id, label, available }) => (
        <button
          key={id}
          onClick={() => available && onChange(id)}
          disabled={switching || provider === id || !available}
          title={!available ? `Requires API key — add to .env` : label}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-all border',
            provider === id
              ? 'border-dg-accent bg-dg-accent/10 text-dg-accent'
              : !available
                ? 'border-dg-border/30 text-dg-muted/40 cursor-not-allowed'
                : 'border-dg-border text-dg-muted hover:border-dg-text hover:text-white'
          )}
        >
          {switching && provider === id
            ? <Loader2 className="w-3 h-3 animate-spin" />
            : <span className={cn('w-1.5 h-1.5 rounded-full', provider === id ? 'bg-dg-accent' : 'bg-dg-muted/40')} />
          }
          {label}
        </button>
      ))}
      {switching && <span className="text-xs text-dg-muted font-mono ml-auto">Switching provider…</span>}
    </div>
  )
}

function DocCard({ doc, index }) {
  const [open, setOpen] = useState(false)
  const isPoisoned = doc.id?.startsWith('poison-') || doc.metadata?.source === 'upload'
  const isPdf = isPoisoned && doc.metadata?.filename?.endsWith('.pdf')
  const stripped = doc.metadata?._injection_stripped

  return (
    <div className={cn(
      'rounded-lg border text-xs',
      isPoisoned ? 'border-dg-poison/50 bg-dg-poison/5' : 'border-dg-border bg-dg-surface'
    )}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          {isPoisoned
            ? <AlertTriangle className="w-3.5 h-3.5 text-dg-poison flex-none" />
            : <CheckCircle className="w-3.5 h-3.5 text-dg-clean flex-none" />
          }
          <span className={cn('font-medium truncate', isPoisoned ? 'text-dg-poison' : 'text-dg-text')}>
            {doc.metadata?.title || `Doc ${index + 1}`}
          </span>
          {stripped && <span className="text-dg-defend text-[10px] font-mono bg-dg-defend/10 px-1.5 py-0.5 rounded">STRIPPED</span>}
          {isPoisoned && <span className="text-dg-poison text-[10px] font-mono bg-dg-poison/10 px-1.5 py-0.5 rounded">INJECTION</span>}
          {isPdf && <span className="text-orange-400 text-[10px] font-mono bg-orange-500/10 px-1.5 py-0.5 rounded border border-orange-500/20">PDF</span>}
        </div>
        {open ? <ChevronUp className="w-3 h-3 text-dg-muted flex-none" /> : <ChevronDown className="w-3 h-3 text-dg-muted flex-none" />}
      </button>
      {open && (
        <div className={cn(
          'px-3 pb-3 font-mono text-[11px] leading-relaxed whitespace-pre-wrap border-t',
          isPoisoned ? 'border-dg-poison/20 text-dg-poison/80' : 'border-dg-border text-dg-muted'
        )}>
          {doc.text}
        </div>
      )}
    </div>
  )
}

const SEVERITY_COLORS = {
  Critical: 'text-red-400 bg-red-400/10 border-red-400/30',
  High:     'text-dg-poison bg-dg-poison/10 border-dg-poison/30',
  Medium:   'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  Low:      'text-dg-clean bg-dg-clean/10 border-dg-clean/30',
  None:     'text-dg-muted bg-transparent border-dg-border/30',
}

function ScoresPanel() {
  const [scores, setScores] = useState([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open && scores.length === 0) {
      api.getScores().then(setScores).catch(() => {})
    }
  }, [open])

  return (
    <div className="flex-none border border-dg-border/40 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-[11px] font-mono text-dg-muted hover:text-white transition-colors bg-dg-surface/40"
      >
        <span className="flex items-center gap-1.5 uppercase tracking-wider">
          <Zap className="w-3 h-3" /> CVSS Attack Scores
        </span>
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>
      {open && (
        <div className="max-h-48 overflow-y-auto">
          {scores.length === 0
            ? <p className="text-dg-muted text-xs italic px-3 py-2">Loading…</p>
            : (
              <table className="w-full text-[10px] font-mono">
                <thead>
                  <tr className="border-b border-dg-border/40 text-dg-muted">
                    <th className="text-left px-3 py-1">ID</th>
                    <th className="text-left px-3 py-1">Score</th>
                    <th className="text-left px-3 py-1">Severity</th>
                    <th className="text-left px-3 py-1 hidden sm:table-cell">Vector</th>
                  </tr>
                </thead>
                <tbody>
                  {scores.map((s) => (
                    <tr key={s.scenario_id} className="border-b border-dg-border/20 hover:bg-dg-surface/30">
                      <td className="px-3 py-1 font-bold text-dg-text">{s.scenario_id}</td>
                      <td className="px-3 py-1 text-dg-text">{s.base_score.toFixed(1)}</td>
                      <td className="px-3 py-1">
                        <span className={`px-1.5 py-0.5 rounded border text-[9px] font-semibold ${SEVERITY_COLORS[s.severity] || ''}`}>
                          {s.severity}
                        </span>
                      </td>
                      <td className="px-3 py-1 text-dg-muted hidden sm:table-cell truncate max-w-[120px]" title={s.description}>
                        {s.description.slice(0, 40)}…
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          }
        </div>
      )}
    </div>
  )
}

function AttackConsole({ lastResult, logs, mode, onClearLogs, loadingLogs }) {
  const modeInfo = MODES.find((m) => m.id === mode) || MODES[0]
  const ModeIcon = modeInfo.Icon
  const attackCount  = logs.filter((l) => l.event === 'injection_retrieved').length
  const blockedCount = logs.filter((l) => l.event === 'injection_blocked').length
  const totalQueries = logs.filter((l) => l.event === 'query').length

  const asrPct       = totalQueries > 0 ? Math.round(attackCount  / totalQueries  * 100) : null
  const blockPct     = attackCount  > 0 ? Math.round(blockedCount / attackCount   * 100) : null

  return (
    <div className="flex flex-col gap-3 h-full overflow-hidden">
      {/* Status bar */}
      <div className={cn(
        'flex items-center gap-3 p-3 rounded-lg border text-xs',
        mode === 'clean'    ? 'border-dg-clean/30 bg-dg-clean/5' :
        mode === 'poisoned' ? 'border-dg-poison/30 bg-dg-poison/5' :
                              'border-dg-defend/30 bg-dg-defend/5'
      )}>
        <ModeIcon className={cn(
          'w-4 h-4 flex-none',
          mode === 'clean' ? 'text-dg-clean' : mode === 'poisoned' ? 'text-dg-poison' : 'text-dg-defend'
        )} />
        <div>
          <div className={cn(
            'font-semibold',
            mode === 'clean' ? 'text-dg-clean' : mode === 'poisoned' ? 'text-dg-poison' : 'text-dg-defend'
          )}>{modeInfo.label} Mode</div>
          <div className="text-dg-muted">{modeInfo.desc}</div>
        </div>
        <div className="ml-auto flex gap-4 text-right font-mono">
          <div>
            <div className="text-dg-muted text-[10px] uppercase tracking-wider mb-0.5">Queries</div>
            <div className="text-dg-text font-bold text-base">{totalQueries}</div>
          </div>
          <div>
            <div className="text-dg-muted text-[10px] uppercase tracking-wider mb-0.5">
              ASR{asrPct !== null ? ` ${asrPct}%` : ''}
            </div>
            <div className="text-dg-poison font-bold text-base">{attackCount}</div>
          </div>
          <div>
            <div className="text-dg-muted text-[10px] uppercase tracking-wider mb-0.5">
              Blocked{blockPct !== null ? ` ${blockPct}%` : ''}
            </div>
            <div className="text-dg-defend font-bold text-base">{blockedCount}</div>
          </div>
        </div>
      </div>

      {/* Retrieved context */}
      {lastResult && (
        <div className="flex-none">
          <div className="text-[11px] font-mono text-dg-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Eye className="w-3 h-3" /> Retrieved Context
            {lastResult.injection_detected && (
              <span className="ml-auto text-dg-defend">injection detected + stripped</span>
            )}
          </div>
          <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
            {lastResult.retrieved_docs?.length > 0
              ? lastResult.retrieved_docs.map((d, i) => <DocCard key={d.id} doc={d} index={i} />)
              : <p className="text-dg-muted text-xs italic">No docs retrieved</p>
            }
          </div>
        </div>
      )}

      {/* Tool calls */}
      {lastResult?.tool_calls?.length > 0 && (
        <div className="flex-none">
          <div className="text-[11px] font-mono text-dg-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Zap className="w-3 h-3" /> Tool Calls
          </div>
          <div className="space-y-1">
            {lastResult.tool_calls.map((tc, i) => (
              <div key={i} className="flex items-start gap-2 bg-dg-surface border border-dg-border rounded-lg px-3 py-2 text-xs">
                <Zap className="w-3 h-3 text-dg-accent mt-0.5 flex-none" />
                <div className="min-w-0">
                  <span className="font-mono text-dg-accent font-medium">{tc.name}</span>
                  {Object.keys(tc.input).length > 0 && (
                    <span className="text-dg-muted ml-2">{JSON.stringify(tc.input).slice(0, 60)}</span>
                  )}
                  {tc.output && (
                    <div className="text-dg-muted mt-1 truncate">{tc.output.slice(0, 120)}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CVSS Scores panel */}
      <ScoresPanel />

      {/* Attack log */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="text-[11px] font-mono text-dg-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <AlertTriangle className="w-3 h-3" /> Attack Log
          <button onClick={onClearLogs} className="ml-auto text-dg-muted hover:text-white transition-colors">
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto space-y-1 min-h-0 pr-1">
          {loadingLogs && <p className="text-dg-muted text-xs italic">Loading…</p>}
          {!loadingLogs && logs.length === 0 && (
            <p className="text-dg-muted text-xs italic">No events yet — send a query</p>
          )}
          {logs.map((log) => {
            const isAttack    = log.event === 'injection_retrieved'
            const isBlocked   = log.event === 'injection_blocked'
            const isModeChange = log.event === 'mode_change'
            const isHashFail  = log.event === 'hash_mismatch'
            const isCapDenied = log.event === 'capability_denied'
            const isTampered  = log.event === 'tool_description_tampered'
            const isWarning   = isHashFail || isCapDenied || isTampered
            return (
              <div key={log.id} className={cn(
                'flex items-start gap-2 rounded px-2.5 py-1.5 text-[11px] font-mono border',
                isAttack   ? 'border-dg-poison/30 bg-dg-poison/5 text-dg-poison' :
                isBlocked  ? 'border-dg-defend/30 bg-dg-defend/5 text-dg-defend' :
                isWarning  ? 'border-yellow-500/30 bg-yellow-500/5 text-yellow-400' :
                isModeChange ? 'border-dg-accent/30 bg-dg-accent/5 text-dg-accent' :
                               'border-dg-border/40 bg-transparent text-dg-muted'
              )}>
                {isAttack   ? <XCircle className="w-3 h-3 mt-0.5 flex-none" /> :
                 isBlocked  ? <ShieldCheck className="w-3 h-3 mt-0.5 flex-none" /> :
                 isWarning  ? <AlertTriangle className="w-3 h-3 mt-0.5 flex-none" /> :
                              <span className="w-3 h-3 flex-none" />}
                <div className="min-w-0">
                  <span className="font-semibold">{log.event}</span>
                  <span className="ml-2 text-inherit/70">{log.detail.slice(0, 80)}</span>
                  <div className="opacity-50 text-[10px]">{log.timestamp.slice(11, 19)} UTC</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default function AttackLab() {
  const [mode, setMode] = useState('clean')
  const [switching, setSwitching] = useState(false)
  const [provider, setProvider] = useState('ollama')
  const [providers, setProviders] = useState([
    { id: 'ollama', label: 'Ollama', available: true },
    { id: 'gemini', label: 'Gemini', available: false },
    { id: 'claude', label: 'Claude', available: false },
  ])
  const [switchingProvider, setSwitchingProvider] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [lastResult, setLastResult] = useState(null)
  const [logs, setLogs] = useState([])
  const [loadingLogs, setLoadingLogs] = useState(false)
  const [uploadingPdf, setUploadingPdf] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Poll logs every 3s
  useEffect(() => {
    fetchLogs()
    const id = setInterval(fetchLogs, 3000)
    return () => clearInterval(id)
  }, [])

  // Fetch initial mode + providers
  useEffect(() => {
    api.getMode().then((r) => setMode(r.mode)).catch(() => {})
    api.getProviders().then((list) => setProviders(list)).catch(() => {})
    api.getProvider().then((r) => setProvider(r.provider)).catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  useEffect(() => {
    const t = textareaRef.current
    if (!t) return
    t.style.height = 'auto'
    t.style.height = `${Math.min(t.scrollHeight, 120)}px`
  }, [input])

  async function fetchLogs() {
    try {
      const data = await api.getLogs()
      setLogs(data)
    } catch {}
  }

  async function handleDemoPoisonUpload() {
    if (uploadingPdf) return
    setUploadingPdf(true)
    try {
      await api.ingestDemoPoison()
      fetchLogs()
    } catch (e) {
      alert(`Demo poison upload failed: ${e.message}`)
    } finally {
      setUploadingPdf(false)
    }
  }

  async function handleProviderChange(newProvider) {
    if (newProvider === provider || switchingProvider) return
    setSwitchingProvider(true)
    try {
      const res = await api.setProvider(newProvider)
      setProvider(res.provider)
    } catch (e) {
      alert(`Provider switch failed: ${e.message}`)
    } finally {
      setSwitchingProvider(false)
    }
  }

  async function handleModeChange(newMode) {
    if (newMode === mode || switching) return
    setSwitching(true)
    try {
      const res = await api.setMode(newMode)
      setMode(res.mode)
    } catch (e) {
      alert(`Mode switch failed: ${e.message}`)
    } finally {
      setSwitching(false)
      fetchLogs()
    }
  }

  async function handleSend() {
    const text = input.trim()
    if (!text || sending) return
    setSending(true)
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    try {
      const res = await api.query(text, SESSION_ID)
      setLastResult(res)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer, meta: res }])
      fetchLogs()
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
    } finally {
      setSending(false)
    }
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] overflow-hidden">
      <ModeBar mode={mode} onChange={handleModeChange} switching={switching} />
      <ModelBar provider={provider} providers={providers} onChange={handleProviderChange} switching={switchingProvider} />

      <div className="flex-1 flex gap-0 overflow-hidden">
        {/* ── Left: Chat ── */}
        <div className="flex-1 flex flex-col border-r border-dg-border overflow-hidden">
          <div className="px-4 py-2 border-b border-dg-border bg-dg-blue/10 flex-none">
            <p className="text-xs text-dg-muted font-mono">RESEARCHER VIEW — PharmaHelp Chat</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && !sending && (
              <div className="space-y-2 pt-4">
                <p className="text-xs text-dg-muted font-mono mb-4">Try a query — switch modes to see the attack:</p>
                {DEMO_PROMPTS.map((p) => (
                  <button
                    key={p}
                    onClick={() => { setInput(p); textareaRef.current?.focus() }}
                    className="block w-full text-left text-xs text-dg-text p-2.5 rounded-lg border border-dg-border hover:border-dg-accent/40 hover:bg-dg-surface transition-all"
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={cn('flex gap-2 animate-fade-in', m.role === 'user' ? 'justify-end' : 'justify-start')}>
                {m.role === 'assistant' && (
                  <div className="w-6 h-6 rounded bg-dg-accent/20 flex items-center justify-center flex-none mt-0.5">
                    <Bot className="w-3.5 h-3.5 text-dg-accent" />
                  </div>
                )}
                <div className={cn(
                  'max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed',
                  m.role === 'user'
                    ? 'bg-dg-accent text-white rounded-tr-sm'
                    : m.meta?.injection_detected
                      ? 'bg-dg-defend/10 border border-dg-defend/40 text-dg-text rounded-tl-sm'
                      : 'bg-dg-surface border border-dg-border text-dg-text rounded-tl-sm'
                )}>
                  {m.content}
                  {m.role === 'assistant' && m.meta && (
                    <div className="flex items-center gap-2 mt-1.5 text-[10px] font-mono text-dg-muted/60">
                      {m.meta.injection_detected && (
                        <span className="flex items-center gap-1 text-dg-defend">
                          <ShieldCheck className="w-2.5 h-2.5" /> injection stripped
                        </span>
                      )}
                      {m.meta.turn_count > 1 && (
                        <span className="flex items-center gap-1">
                          turn {m.meta.turn_count}
                          {m.meta.mode === 'defended' && ' · context isolated'}
                        </span>
                      )}
                      {m.meta.provider && (
                        <span className="flex items-center gap-1 ml-auto">
                          <Cpu className="w-2.5 h-2.5" /> via {m.meta.provider}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                {m.role === 'user' && (
                  <div className="w-6 h-6 rounded bg-dg-orange/20 flex items-center justify-center flex-none mt-0.5">
                    <User className="w-3.5 h-3.5 text-dg-orange" />
                  </div>
                )}
              </div>
            ))}

            {sending && (
              <div className="flex gap-2 justify-start">
                <div className="w-6 h-6 rounded bg-dg-accent/20 flex items-center justify-center flex-none">
                  <Bot className="w-3.5 h-3.5 text-dg-accent" />
                </div>
                <div className="bg-dg-surface border border-dg-border rounded-xl rounded-tl-sm px-3 py-2 flex gap-1">
                  {[0, 150, 300].map((d) => (
                    <span key={d} className="w-1.5 h-1.5 rounded-full bg-dg-accent animate-bounce" style={{ animationDelay: `${d}ms` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="flex-none p-3 border-t border-dg-border">
            <div className="relative rounded-lg border border-dg-border bg-dg-surface focus-within:border-dg-accent/50 transition-colors">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKey}
                placeholder="Ask a research question…"
                rows={1}
                className="w-full resize-none bg-transparent px-3 py-2.5 pr-10 text-xs text-dg-text placeholder-dg-muted focus:outline-none"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || sending}
                className={cn(
                  'absolute right-2 bottom-2 p-1.5 rounded transition-all',
                  input.trim() && !sending
                    ? 'bg-dg-accent text-white hover:bg-dg-accent/80'
                    : 'text-dg-muted cursor-not-allowed'
                )}
              >
                {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>

        {/* ── Right: Attack Console ── */}
        <div className="w-96 flex flex-col overflow-hidden bg-dg-blue/10">
          <div className="px-4 py-2 border-b border-dg-border bg-dg-blue/10 flex-none flex items-center justify-between">
            <p className="text-xs text-dg-muted font-mono">ATTACK CONSOLE</p>
            <div className="flex items-center gap-2">
              <button
                onClick={handleDemoPoisonUpload}
                disabled={uploadingPdf}
                className="text-xs font-mono px-2 py-1 rounded border border-orange-500/30 text-orange-400 hover:bg-orange-500/10 disabled:opacity-40 transition-colors"
              >
                {uploadingPdf ? 'Uploading…' : '↑ Demo Poison PDF'}
              </button>
              <button onClick={fetchLogs} className="text-dg-muted hover:text-white transition-colors">
                <RefreshCw className="w-3 h-3" />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-hidden p-3">
            <AttackConsole
              lastResult={lastResult}
              logs={logs}
              mode={mode}
              onClearLogs={async () => { await api.clearLogs(); fetchLogs() }}
              loadingLogs={loadingLogs}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
