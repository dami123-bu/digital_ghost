import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles, Paperclip, Database, X } from 'lucide-react'
import { cn } from '../lib/utils'
import { api } from '../lib/api'

const SESSION_ID = crypto.randomUUID()

const PROMPTS = [
  'What is the IC50 of compound DGX-4?',
  'Which drug has the best safety profile for oncology?',
  'Summarise the latest compound approval pipeline',
  'What are the toxicity findings for imatinib?',
]

export default function Chat() {
  const [messages, setMessages]       = useState([])
  const [input, setInput]             = useState('')
  const [sending, setSending]         = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)  // null | 'uploading' | 'done' | 'error'
  const [uploadMsg, setUploadMsg]     = useState('')
  const [attachedFile, setAttachedFile] = useState(null)  // file attached for ephemeral query
  const bottomRef    = useRef(null)
  const textareaRef  = useRef(null)
  const fileInputRef = useRef(null)   // ephemeral attach (paperclip)
  const kbFileInputRef = useRef(null) // persistent KB ingest (Add to KB)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  useEffect(() => {
    const t = textareaRef.current
    if (!t) return
    t.style.height = 'auto'
    t.style.height = `${Math.min(t.scrollHeight, 180)}px`
  }, [input])

  async function handleSend() {
    const text = input.trim()
    if (!text || sending) return
    setSending(true)
    const file = attachedFile
    setAttachedFile(null)
    setMessages((prev) => [...prev, { role: 'user', content: text, attachedFile: file?.name }])
    setInput('')
    try {
      const res = file
        ? await api.queryWithDoc(text, SESSION_ID, file)
        : await api.query(text, SESSION_ID)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer, meta: res }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
    } finally {
      setSending(false)
    }
  }

  // Ephemeral attach — file is held in state and sent with the next query only.
  // It is never stored in ChromaDB.
  function handleAttachFile(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setAttachedFile(file)
    e.target.value = ''
  }

  // Persistent KB ingest — file is chunked and stored in ChromaDB immediately.
  // Every user and future session can retrieve it.
  async function handleAddToKB(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadStatus('uploading')
    setUploadMsg(`Adding "${file.name}" to knowledge base…`)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await api.ingest(fd)
      setUploadMsg(`"${res.filename}" — ${res.chunks_stored} chunk(s) added to ${res.mode} KB (persistent)`)
      setUploadStatus('done')
    } catch (err) {
      setUploadMsg(`Upload failed: ${err.message}`)
      setUploadStatus('error')
    }
    setTimeout(() => { setUploadStatus(null); setUploadMsg('') }, 5000)
    e.target.value = ''
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4 py-4 gap-4 h-[calc(100vh-3.5rem)] overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 && !sending && (
          <div className="flex flex-col items-center justify-center h-full gap-8 animate-fade-in">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-xl bg-dg-accent/10 flex items-center justify-center mx-auto">
                <Sparkles className="w-6 h-6 text-dg-accent" />
              </div>
              <h2 className="text-xl font-semibold text-white">PharmaHelp</h2>
              <p className="text-dg-muted text-sm">BioForge Research Assistant</p>
            </div>
            <div className="grid grid-cols-2 gap-2 w-full max-w-md">
              {PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => { setInput(p); textareaRef.current?.focus() }}
                  className="text-left text-xs text-dg-text p-3 rounded-lg border border-dg-border hover:border-dg-accent/40 hover:bg-dg-surface transition-all"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={cn('flex gap-3 animate-fade-in', m.role === 'user' ? 'justify-end' : 'justify-start')}>
            {m.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-dg-accent/20 flex items-center justify-center flex-none mt-0.5">
                <Bot className="w-4 h-4 text-dg-accent" />
              </div>
            )}
            <div className={cn(
              'max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed',
              m.role === 'user'
                ? 'bg-dg-accent text-white rounded-tr-sm'
                : 'bg-dg-surface border border-dg-border text-dg-text rounded-tl-sm'
            )}>
              {m.role === 'user' && m.attachedFile && (
                <div className="flex items-center gap-1 text-[10px] font-mono text-white/60 mb-1">
                  <Paperclip className="w-2.5 h-2.5" />
                  {m.attachedFile}
                  <span className="text-white/40 ml-1">(ephemeral)</span>
                </div>
              )}
              {m.content}
              {m.role === 'assistant' && m.meta?.turn_count > 1 && (
                <div className="text-[10px] font-mono text-dg-muted/50 mt-1.5">
                  turn {m.meta.turn_count}
                </div>
              )}
            </div>
            {m.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-dg-orange/20 flex items-center justify-center flex-none mt-0.5">
                <User className="w-4 h-4 text-dg-orange" />
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex gap-3 justify-start animate-fade-in">
            <div className="w-7 h-7 rounded-lg bg-dg-accent/20 flex items-center justify-center flex-none">
              <Bot className="w-4 h-4 text-dg-accent" />
            </div>
            <div className="bg-dg-surface border border-dg-border rounded-xl rounded-tl-sm px-4 py-3 flex gap-1">
              {[0, 150, 300].map((d) => (
                <span key={d} className="w-1.5 h-1.5 rounded-full bg-dg-accent animate-bounce" style={{ animationDelay: `${d}ms` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-none space-y-1.5">
        {/* Attached file badge (ephemeral) */}
        {attachedFile && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono border bg-dg-accent/10 border-dg-accent/20 text-dg-accent">
            <Paperclip className="w-3 h-3 flex-none" />
            <span className="truncate">{attachedFile.name}</span>
            <span className="text-dg-accent/50">— attached for this query only</span>
            <button
              onClick={() => setAttachedFile(null)}
              className="ml-auto hover:text-white transition-colors"
              title="Remove attachment"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* KB upload status bar */}
        {uploadStatus && (
          <div className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono border',
            uploadStatus === 'error'
              ? 'bg-red-500/10 border-red-500/20 text-red-400'
              : uploadStatus === 'uploading'
              ? 'bg-dg-orange/10 border-dg-orange/20 text-dg-orange'
              : 'bg-green-500/10 border-green-500/20 text-green-400'
          )}>
            <Database className="w-3 h-3 flex-none" />
            {uploadMsg}
          </div>
        )}

        <div className="relative rounded-xl border border-dg-border bg-dg-surface focus-within:border-dg-accent/50 transition-colors">
          {/* Hidden file inputs */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            className="hidden"
            onChange={handleAttachFile}
          />
          <input
            ref={kbFileInputRef}
            type="file"
            accept=".pdf,.txt"
            className="hidden"
            onChange={handleAddToKB}
          />

          {/* Paperclip — ephemeral attach (this query only, not stored) */}
          <button
            onClick={() => fileInputRef.current?.click()}
            title="Attach file to this query (ephemeral — not stored in KB)"
            className={cn(
              'absolute left-2.5 bottom-2.5 p-1.5 rounded-lg transition-colors',
              attachedFile
                ? 'text-dg-accent bg-dg-accent/10'
                : 'text-dg-muted hover:text-white hover:bg-white/10'
            )}
          >
            <Paperclip className="w-3.5 h-3.5" />
          </button>

          {/* Database icon — persistent KB ingest (all users, all sessions) */}
          <button
            onClick={() => kbFileInputRef.current?.click()}
            disabled={uploadStatus === 'uploading'}
            title="Add to knowledge base (persistent — all users and sessions)"
            className="absolute left-9 bottom-2.5 p-1.5 rounded-lg text-dg-muted hover:text-dg-orange hover:bg-white/10 disabled:opacity-40 transition-colors"
          >
            <Database className="w-3.5 h-3.5" />
          </button>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Ask about compounds, trials, LIMS data…"
            rows={1}
            className="w-full resize-none bg-transparent pl-16 pr-12 py-3 text-sm text-dg-text placeholder-dg-muted focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className={cn(
              'absolute right-2.5 bottom-2.5 p-2 rounded-lg transition-all',
              input.trim() && !sending
                ? 'bg-dg-accent text-white hover:bg-dg-accent/80'
                : 'bg-dg-border text-dg-muted cursor-not-allowed'
            )}
          >
            {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  )
}
