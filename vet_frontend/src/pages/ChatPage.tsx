import { useState, useEffect, useRef, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import './ChatPage.css'

// ── Types ──────────────────────────────────────────────────────────────────────

interface VetInfo {
  vetID: string
  name: string
  specialisation: string | null
}

interface MessageItem {
  messageID: string
  senderID: string
  content: string
  timestamp: string
  chatID: string
}

interface Chat {
  chatID: string
  createdAt: string
  isUrgent: boolean
  petOwnerID: string
  vetID: string
  messages?: MessageItem[]
}

// ── API helper ─────────────────────────────────────────────────────────────────

function apiFetch(path: string, options?: RequestInit) {
  const token = localStorage.getItem('token') ?? ''
  return fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options?.headers ?? {}),
    },
  })
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function ChatPage() {
  const navigate = useNavigate()
  const role   = localStorage.getItem('userRole') ?? ''
  const userID = localStorage.getItem('userID')   ?? ''

  // Chat list
  const [chats, setChats]               = useState<Chat[]>([])
  const [activeChatID, setActiveChatID] = useState<string | null>(null)
  const [activeChat, setActiveChat]     = useState<Chat | null>(null)

  // Send message
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)

  // New-chat modal
  const [showModal, setShowModal]     = useState(false)
  const [vets, setVets]               = useState<VetInfo[]>([])
  const [selectedVet, setSelectedVet] = useState('')
  const [isUrgent, setIsUrgent]       = useState(false)
  const [starting, setStarting]       = useState(false)
  const [modalError, setModalError]   = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // ── Auth guard ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login?redirect=/vet-advice/chat')
    }
  }, [navigate])

  // ── Load chat list ───────────────────────────────────────────────────────────
  const loadChats = async () => {
    try {
      const res  = await apiFetch('/api/chats')
      const body = await res.json()
      if (res.ok) setChats(body.data as Chat[])
    } catch { /* network error — silently ignore */ }
  }

  useEffect(() => { loadChats() }, [])

  // ── Load active chat ─────────────────────────────────────────────────────────
  const loadActiveChat = async (id: string) => {
    try {
      const res  = await apiFetch(`/api/chats/${id}`)
      const body = await res.json()
      if (res.ok) setActiveChat(body.data as Chat)
    } catch { /* ignore */ }
  }

  // ── Subscribe via WebSocket (Observer pattern) ────────────────────────────────
  useEffect(() => {
    if (!activeChatID) return
    loadActiveChat(activeChatID)

    const wsUrl = `ws://localhost:8000/api/chats/${activeChatID}/ws`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (e) => {
      const { event, data } = JSON.parse(e.data) as { event: string; data: MessageItem }
      if (event === 'message_sent') {
        setActiveChat(prev =>
          prev ? { ...prev, messages: [...(prev.messages ?? []), data] } : prev
        )
      }
    }

    return () => ws.close()
  }, [activeChatID])

  // ── Scroll to bottom on new messages ────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeChat?.messages?.length])

  // ── Open new-chat modal ───────────────────────────────────────────────────────
  const openModal = async () => {
    setModalError(null)
    setSelectedVet('')
    setIsUrgent(false)
    try {
      const res  = await apiFetch('/api/vets')
      const body = await res.json()
      if (res.ok) setVets(body.data as VetInfo[])
    } catch { /* ignore */ }
    setShowModal(true)
  }

  // ── Start chat ────────────────────────────────────────────────────────────────
  const startChat = async () => {
    if (!selectedVet) return
    setStarting(true)
    setModalError(null)
    try {
      const res  = await apiFetch('/api/chats', {
        method: 'POST',
        body:   JSON.stringify({ vetID: selectedVet, isUrgent }),
      })
      const body = await res.json()
      if (res.ok) {
        setShowModal(false)
        await loadChats()
        setActiveChatID(body.data.chatID)
      } else {
        setModalError(body.detail ?? 'Failed to start chat.')
      }
    } catch {
      setModalError('Could not reach server.')
    } finally {
      setStarting(false)
    }
  }

  // ── Send message ──────────────────────────────────────────────────────────────
  const sendMessage = async (e: FormEvent) => {
    e.preventDefault()
    if (!message.trim() || !activeChatID) return
    setSending(true)
    try {
      const res = await apiFetch(`/api/chats/${activeChatID}/messages`, {
        method: 'POST',
        body:   JSON.stringify({ content: message.trim() }),
      })
      if (res.ok) {
        setMessage('')
        await loadActiveChat(activeChatID)
      }
    } catch { /* ignore */ }
    setSending(false)
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="chat-page">

      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="chat-sidebar">
        <div className="chat-sidebar__header">
          <h2>Chats</h2>
          {role === 'pet_owner' && (
            <button className="btn btn--primary btn--sm" onClick={openModal}>
              + New
            </button>
          )}
        </div>

        {chats.length === 0 ? (
          <p className="chat-sidebar__empty">No chats yet.</p>
        ) : (
          <ul className="chat-list">
            {chats.map(c => (
              <li
                key={c.chatID}
                className={`chat-list__item${activeChatID === c.chatID ? ' chat-list__item--active' : ''}`}
                onClick={() => setActiveChatID(c.chatID)}
              >
                <span className="chat-list__id">Chat #{c.chatID.slice(0, 8)}</span>
                {c.isUrgent && <span className="chat-list__urgent">URGENT</span>}
                <span className="chat-list__date">{c.createdAt.slice(0, 10)}</span>
              </li>
            ))}
          </ul>
        )}
      </aside>

      {/* ── Main panel ───────────────────────────────────────────────────── */}
      <main className="chat-main">
        {!activeChatID ? (
          <div className="chat-empty">
            <span>💬</span>
            <p>Select a chat from the left, or start a new one.</p>
          </div>
        ) : (
          <>
            <div className="chat-messages">
              {(activeChat?.messages ?? []).map(m => (
                <div
                  key={m.messageID}
                  className={`chat-bubble${m.senderID === userID ? ' chat-bubble--mine' : ' chat-bubble--theirs'}`}
                >
                  <p>{m.content}</p>
                  <span className="chat-bubble__time">
                    {m.timestamp.length >= 16 ? m.timestamp.slice(11, 16) : m.timestamp}
                  </span>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input" onSubmit={sendMessage}>
              <input
                type="text"
                placeholder="Type a message…"
                value={message}
                onChange={e => setMessage(e.target.value)}
                disabled={sending}
                autoComplete="off"
              />
              <button
                type="submit"
                className="btn btn--primary"
                disabled={sending || !message.trim()}
              >
                Send
              </button>
            </form>
          </>
        )}
      </main>

      {/* ── New-chat modal ────────────────────────────────────────────────── */}
      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Start a New Chat</h3>

            {modalError && <p className="modal__error">{modalError}</p>}

            <div className="form-group">
              <label htmlFor="vet-select">Veterinarian</label>
              <select
                id="vet-select"
                value={selectedVet}
                onChange={e => setSelectedVet(e.target.value)}
              >
                <option value="">— choose a vet —</option>
                {vets.map(v => (
                  <option key={v.vetID} value={v.vetID}>
                    {v.name}{v.specialisation ? ` – ${v.specialisation}` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group form-group--inline">
              <input
                type="checkbox"
                id="urgent"
                checked={isUrgent}
                onChange={e => setIsUrgent(e.target.checked)}
              />
              <label htmlFor="urgent">Mark as urgent</label>
            </div>

            <div className="modal__actions">
              <button
                className="btn btn--secondary"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn--primary"
                onClick={startChat}
                disabled={starting || !selectedVet}
              >
                {starting ? 'Starting…' : 'Start Chat'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
