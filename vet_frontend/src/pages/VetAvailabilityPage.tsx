import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './VetAvailabilityPage.css'

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

// Convert datetime-local value ("2026-06-01T09:00") → ISO 8601 ("2026-06-01T09:00:00Z")
function toISO(local: string): string {
  return local.length === 16 ? `${local}:00Z` : local
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function VetAvailabilityPage() {
  const navigate = useNavigate()
  const userID   = localStorage.getItem('userID') ?? ''

  const [slots, setSlots]   = useState<string[]>([])
  const [newSlot, setNewSlot] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg]       = useState<{ type: 'ok' | 'err'; text: string } | null>(null)
  const [loading, setLoading] = useState(true)

  // ── Auth guard + load current slots ─────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('token')
    const role  = localStorage.getItem('userRole')
    if (!token || role !== 'veterinarian') {
      navigate('/login')
      return
    }
    apiFetch('/api/vets')
      .then(r => r.json())
      .then(body => {
        interface VetEntry { vetID: string; availableSlots: string[] }
        const me = (body.data as VetEntry[]).find(v => v.vetID === userID)
        if (me) setSlots(me.availableSlots ?? [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [navigate, userID])

  // ── Add slot ─────────────────────────────────────────────────────────────────
  const addSlot = () => {
    if (!newSlot) return
    const iso = toISO(newSlot)
    if (slots.includes(iso)) return
    setSlots(prev => [...prev, iso].sort())
    setNewSlot('')
  }

  // ── Remove slot ──────────────────────────────────────────────────────────────
  const removeSlot = (s: string) => {
    setSlots(prev => prev.filter(x => x !== s))
  }

  // ── Save to backend ──────────────────────────────────────────────────────────
  const save = async () => {
    setSaving(true)
    setMsg(null)
    try {
      const res = await apiFetch('/api/vets/availability', {
        method: 'PUT',
        body:   JSON.stringify(slots),
      })
      if (res.ok) {
        setMsg({ type: 'ok', text: 'Availability saved successfully.' })
      } else {
        const body = await res.json()
        setMsg({ type: 'err', text: body.detail ?? 'Save failed.' })
      }
    } catch {
      setMsg({ type: 'err', text: 'Could not reach server.' })
    } finally {
      setSaving(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="avail-page">
      <h1>My Availability</h1>
      <p className="avail-subtitle">
        Add timeslots pet owners can book. Changes are not saved until you click
        "Save Availability".
      </p>

      {msg && (
        <p className={`avail-msg${msg.type === 'ok' ? ' avail-msg--success' : ' avail-msg--error'}`}>
          {msg.text}
        </p>
      )}

      {/* ── Add new slot ───────────────────────────────────────────────── */}
      <div className="avail-add">
        <input
          type="datetime-local"
          className="avail-input"
          value={newSlot}
          onChange={e => setNewSlot(e.target.value)}
        />
        <button
          className="btn btn--secondary"
          onClick={addSlot}
          disabled={!newSlot}
        >
          + Add Slot
        </button>
      </div>

      {/* ── Slot list ──────────────────────────────────────────────────── */}
      {loading ? (
        <p className="avail-empty">Loading…</p>
      ) : slots.length === 0 ? (
        <p className="avail-empty">No slots added yet. Use the picker above to add one.</p>
      ) : (
        <ul className="avail-slots">
          {slots.map(s => (
            <li key={s} className="avail-slot">
              <span className="avail-slot__time">
                {new Date(s).toLocaleString(undefined, {
                  weekday: 'short',
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
              <button
                className="avail-slot__remove"
                onClick={() => removeSlot(s)}
                title="Remove this slot"
                aria-label="Remove slot"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <div className="avail-footer">
        <span className="avail-count">
          {slots.length} slot{slots.length !== 1 ? 's' : ''}
        </span>
        <button
          className="btn btn--primary"
          onClick={save}
          disabled={saving || loading}
        >
          {saving ? 'Saving…' : 'Save Availability'}
        </button>
      </div>
    </div>
  )
}
