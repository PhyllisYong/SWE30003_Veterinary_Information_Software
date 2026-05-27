import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './BookingPage.css'

// ── Types ──────────────────────────────────────────────────────────────────────

interface VetInfo {
  vetID: string
  name: string
  specialisation: string | null
  availableSlots: string[]
}

interface BookingItem {
  bookingID: string
  createdAt: string
  timeslot: string
  bookingStatus: string
  petOwnerID: string
  vetID: string
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

// ── Status badge helper ────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const cls: Record<string, string> = {
    pending:   'badge badge--yellow',
    accepted:  'badge badge--green',
    cancelled: 'badge badge--red',
    completed: 'badge badge--gray',
  }
  return <span className={cls[status] ?? 'badge'}>{status}</span>
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function BookingPage() {
  const navigate = useNavigate()
  const role = localStorage.getItem('userRole') ?? ''

  const [vets, setVets]               = useState<VetInfo[]>([])
  const [bookings, setBookings]       = useState<BookingItem[]>([])
  const [selectedVet, setSelectedVet] = useState<VetInfo | null>(null)
  const [selectedSlot, setSelectedSlot] = useState('')
  const [submitting, setSubmitting]   = useState(false)
  const [error, setError]             = useState<string | null>(null)
  const [success, setSuccess]         = useState<string | null>(null)

  // ── Auth guard ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login?redirect=/vet-advice/booking')
      return
    }
    loadData()
  }, [navigate])

  // ── Load vets + own bookings ─────────────────────────────────────────────────
  const loadData = async () => {
    try {
      const [vetsRes, bookingsRes] = await Promise.all([
        apiFetch('/api/vets'),
        apiFetch('/api/bookings'),
      ])
      const vetsBody     = await vetsRes.json()
      const bookingsBody = await bookingsRes.json()
      if (vetsRes.ok)     setVets(vetsBody.data as VetInfo[])
      if (bookingsRes.ok) setBookings(bookingsBody.data as BookingItem[])
    } catch { /* network error */ }
  }

  // ── Pet owner: make booking ──────────────────────────────────────────────────
  const makeBooking = async () => {
    if (!selectedVet || !selectedSlot) return
    setSubmitting(true)
    setError(null)
    setSuccess(null)
    try {
      const res  = await apiFetch('/api/bookings', {
        method: 'POST',
        body:   JSON.stringify({ vetID: selectedVet.vetID, timeslot: selectedSlot }),
      })
      const body = await res.json()
      if (res.ok) {
        setSuccess(`Booking requested for ${selectedSlot}. Awaiting vet confirmation.`)
        setSelectedVet(null)
        setSelectedSlot('')
        await loadData()
      } else {
        setError(body.detail ?? 'Failed to make booking.')
      }
    } catch {
      setError('Could not reach server.')
    } finally {
      setSubmitting(false)
    }
  }

  // ── Vet: accept a pending booking ────────────────────────────────────────────
  const acceptBooking = async (bookingID: string) => {
    try {
      const res = await apiFetch(`/api/bookings/${bookingID}/accept`, { method: 'PUT' })
      if (res.ok) await loadData()
    } catch { /* ignore */ }
  }

  const pendingBookings = bookings.filter(b => b.bookingStatus === 'pending')

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="booking-page">
      <h1>Physical Consultation</h1>

      {/* ── Pet owner: book a slot ─────────────────────────────────────── */}
      {role === 'pet_owner' && (
        <section className="booking-section">
          <h2>Book an Appointment</h2>

          {error   && <p className="booking-msg booking-msg--error">{error}</p>}
          {success && <p className="booking-msg booking-msg--success">{success}</p>}

          {vets.length === 0 ? (
            <p className="booking-empty">No veterinarians available yet.</p>
          ) : (
            <div className="vet-grid">
              {vets.map(v => (
                <div
                  key={v.vetID}
                  className={`vet-card${selectedVet?.vetID === v.vetID ? ' vet-card--selected' : ''}`}
                  onClick={() => { setSelectedVet(v); setSelectedSlot('') }}
                >
                  <div className="vet-card__name">{v.name}</div>
                  {v.specialisation && (
                    <div className="vet-card__spec">{v.specialisation}</div>
                  )}
                  <div className="vet-card__slots">
                    {v.availableSlots.length} slot{v.availableSlots.length !== 1 ? 's' : ''} available
                  </div>
                </div>
              ))}
            </div>
          )}

          {selectedVet && (
            <div className="slot-picker">
              <h3>Available slots — {selectedVet.name}</h3>
              {selectedVet.availableSlots.length === 0 ? (
                <p className="booking-empty">No available slots for this vet.</p>
              ) : (
                <div className="slot-grid">
                  {selectedVet.availableSlots.map(s => (
                    <button
                      key={s}
                      className={`slot-btn${selectedSlot === s ? ' slot-btn--active' : ''}`}
                      onClick={() => setSelectedSlot(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <div className="slot-picker__actions">
                <button
                  className="btn btn--secondary"
                  onClick={() => { setSelectedVet(null); setSelectedSlot('') }}
                >
                  Cancel
                </button>
                <button
                  className="btn btn--primary"
                  disabled={!selectedSlot || submitting}
                  onClick={makeBooking}
                >
                  {submitting ? 'Booking…' : 'Confirm Booking'}
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      {/* ── Vet: pending requests to accept ───────────────────────────── */}
      {role === 'veterinarian' && (
        <section className="booking-section">
          <h2>Pending Booking Requests</h2>
          {pendingBookings.length === 0 ? (
            <p className="booking-empty">No pending requests.</p>
          ) : (
            <table className="booking-table">
              <thead>
                <tr>
                  <th>Pet Owner</th>
                  <th>Timeslot</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pendingBookings.map(b => (
                  <tr key={b.bookingID}>
                    <td title={b.petOwnerID}>{b.petOwnerID.slice(0, 8)}…</td>
                    <td>{b.timeslot}</td>
                    <td><StatusBadge status={b.bookingStatus} /></td>
                    <td>
                      <button
                        className="btn btn--primary btn--sm"
                        onClick={() => acceptBooking(b.bookingID)}
                      >
                        Accept
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {/* ── All roles: my bookings ─────────────────────────────────────── */}
      <section className="booking-section">
        <h2>My Bookings</h2>
        {bookings.length === 0 ? (
          <p className="booking-empty">No bookings yet.</p>
        ) : (
          <table className="booking-table">
            <thead>
              <tr>
                <th>Booking ID</th>
                <th>Timeslot</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map(b => (
                <tr key={b.bookingID}>
                  <td title={b.bookingID}>{b.bookingID.slice(0, 8)}…</td>
                  <td>{b.timeslot}</td>
                  <td><StatusBadge status={b.bookingStatus} /></td>
                  <td>{b.createdAt.slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
