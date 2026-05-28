import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './VetVideoManagePage.css'

// ── Types ──────────────────────────────────────────────────────────────────────

interface VideoItem {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  publicationStatus: string
  videoURL: string
  durationSec: number | null
}

interface FormState {
  title: string
  description: string
  petType: string
  emergencyCategory: string
  videoURL: string
  durationSec: string
}

const EMPTY_FORM: FormState = {
  title: '',
  description: '',
  petType: 'dog',
  emergencyCategory: 'bleeding',
  videoURL: '',
  durationSec: '',
}

const PET_TYPES = ['dog', 'cat', 'rabbit', 'hamster', 'guinea pig']
const CATEGORIES = ['bleeding', 'choking', 'cpr', 'poisoning', 'fracture', 'heatstroke', 'seizure', 'wound']

// ── Helpers ────────────────────────────────────────────────────────────────────

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

function statusClass(status: string): string {
  const map: Record<string, string> = {
    published: 'badge badge--published',
    verified: 'badge badge--verified',
    pending_verification: 'badge badge--pending',
    rejected: 'badge badge--rejected',
    draft: 'badge badge--draft',
  }
  return map[status] ?? 'badge badge--draft'
}

function statusLabel(status: string): string {
  return status.replace(/_/g, ' ')
}

function capitalise(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function VetVideoManagePage() {
  const navigate = useNavigate()

  const [videos, setVideos]       = useState<VideoItem[]>([])
  const [selected, setSelected]   = useState<VideoItem | null>(null)
  const [isNew, setIsNew]         = useState(false)
  const [form, setForm]           = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)
  const [pageError, setPageError] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [saved, setSaved]         = useState(false)

  // ── Auth guard ───────────────────────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('token')
    const role  = localStorage.getItem('userRole')
    if (!token || role !== 'veterinarian') {
      navigate('/login')
      return
    }
    loadVideos()
  }, [navigate])

  async function loadVideos() {
    setPageError(null)
    try {
      const res  = await apiFetch('/api/content/mine')
      const data = await res.json()
      if (data.status !== 'ok') throw new Error(data.message)
      const videoItems: VideoItem[] = (data.data as any[]).filter(
        (item) => item.content_type === 'video'
      )
      setVideos(videoItems)
    } catch (e: any) {
      setPageError(e.message ?? 'Failed to load videos.')
    }
  }

  // ── Form helpers ─────────────────────────────────────────────────────────────

  function openNew() {
    setSelected(null)
    setIsNew(true)
    setForm(EMPTY_FORM)
    setFormError(null)
    setSaved(false)
  }

  function openEdit(video: VideoItem) {
    setIsNew(false)
    setSelected(video)
    setForm({
      title: video.title,
      description: video.description ?? '',
      petType: video.petType,
      emergencyCategory: video.emergencyCategory,
      videoURL: video.videoURL,
      durationSec: video.durationSec != null ? String(video.durationSec) : '',
    })
    setFormError(null)
    setSaved(false)
  }

  function setField(field: keyof FormState, value: string) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  // ── Submit ────────────────────────────────────────────────────────────────────

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setFormError(null)
    setSaved(false)

    if (!form.title.trim()) {
      setFormError('Title is required.')
      return
    }
    if (!form.videoURL.trim()) {
      setFormError('YouTube URL is required.')
      return
    }

    const authorVetID = localStorage.getItem('userID') ?? ''
    const body = {
      content_type: 'video',
      title: form.title.trim(),
      description: form.description.trim() || null,
      petType: form.petType,
      emergencyCategory: form.emergencyCategory,
      authorVetID,
      videoURL: form.videoURL.trim(),
      durationSec: form.durationSec ? parseInt(form.durationSec, 10) : null,
    }

    setSubmitting(true)
    try {
      const url    = isNew ? '/api/content' : `/api/content/${selected!.contentID}`
      const method = isNew ? 'POST' : 'PUT'
      const res    = await apiFetch(url, { method, body: JSON.stringify(body) })
      const data   = await res.json()
      if (data.status !== 'ok') {
        setFormError(data.message ?? 'Request failed.')
        return
      }
      setSaved(true)
      await loadVideos()
      if (isNew) {
        setIsNew(false)
        setSelected(data.data as VideoItem)
      } else {
        setSelected(data.data as VideoItem)
      }
    } catch (e: any) {
      setFormError(e.message ?? 'Could not reach server.')
    } finally {
      setSubmitting(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  const panelOpen = isNew || selected !== null

  return (
    <div className="vvm-page">
      <h1>Video Library Manager</h1>
      <p className="vvm-subtitle">Submit and manage your first-aid video content.</p>

      {pageError && <p className="vvm-error">{pageError}</p>}

      <div className="vvm-layout">

        {/* ── Sidebar ──────────────────────────────────────────────────── */}
        <aside className="vvm-sidebar">
          <button className="btn btn--primary vvm-add-btn" onClick={openNew}>
            + Add Video
          </button>

          {videos.length === 0 ? (
            <p className="vvm-empty">No videos yet.</p>
          ) : (
            <ul className="vvm-list">
              {videos.map(v => (
                <li
                  key={v.contentID}
                  className={`vvm-item${selected?.contentID === v.contentID && !isNew ? ' vvm-item--active' : ''}`}
                  onClick={() => openEdit(v)}
                >
                  <span className="vvm-item__title">{v.title}</span>
                  <div className="vvm-item__meta">
                    <span>{capitalise(v.petType)} · {v.emergencyCategory}</span>
                    <span className={statusClass(v.publicationStatus)}>
                      {statusLabel(v.publicationStatus)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </aside>

        {/* ── Main panel ───────────────────────────────────────────────── */}
        <main className="vvm-main">
          {!panelOpen ? (
            <div className="vvm-placeholder">
              <span>🎬</span>
              <p>Select a video to edit, or click "+ Add Video".</p>
            </div>
          ) : (
            <form className="vvm-form" onSubmit={handleSubmit} noValidate>
              <h2>{isNew ? 'New Video' : 'Edit Video'}</h2>

              {!isNew && selected && (
                <div className="vvm-status-row">
                  <span>Status: </span>
                  <span className={statusClass(selected.publicationStatus)}>
                    {statusLabel(selected.publicationStatus)}
                  </span>
                </div>
              )}

              {formError && <p className="vvm-error">{formError}</p>}
              {saved && <p className="vvm-success">✓ Saved successfully</p>}

              <label className="vvm-label">
                Title <span className="vvm-required">*</span>
              </label>
              <input
                className="vvm-input"
                type="text"
                placeholder="e.g. CPR for Dogs"
                value={form.title}
                onChange={e => setField('title', e.target.value)}
              />

              <label className="vvm-label">Description</label>
              <textarea
                className="vvm-textarea"
                rows={3}
                placeholder="Brief description of what this video covers…"
                value={form.description}
                onChange={e => setField('description', e.target.value)}
              />

              <div className="vvm-row">
                <div className="vvm-col">
                  <label className="vvm-label">Pet Type</label>
                  <select
                    className="vvm-select"
                    value={form.petType}
                    onChange={e => setField('petType', e.target.value)}
                  >
                    {PET_TYPES.map(pt => (
                      <option key={pt} value={pt}>{capitalise(pt)}</option>
                    ))}
                  </select>
                </div>
                <div className="vvm-col">
                  <label className="vvm-label">Emergency Category</label>
                  <select
                    className="vvm-select"
                    value={form.emergencyCategory}
                    onChange={e => setField('emergencyCategory', e.target.value)}
                  >
                    {CATEGORIES.map(c => (
                      <option key={c} value={c}>{capitalise(c)}</option>
                    ))}
                  </select>
                </div>
              </div>

              <label className="vvm-label">
                YouTube URL <span className="vvm-required">*</span>
              </label>
              <input
                className="vvm-input"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                value={form.videoURL}
                onChange={e => setField('videoURL', e.target.value)}
              />
              <p className="vvm-hint">Paste any YouTube watch or short URL. Stored as embed URL.</p>

              <label className="vvm-label">Duration (seconds)</label>
              <input
                className="vvm-input vvm-input--short"
                type="number"
                min={1}
                placeholder="e.g. 240"
                value={form.durationSec}
                onChange={e => setField('durationSec', e.target.value)}
              />

              <div className="vvm-form__footer">
                <button
                  type="submit"
                  className="btn btn--primary"
                  disabled={submitting}
                >
                  {submitting ? 'Saving…' : isNew ? 'Submit Video' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}
        </main>

      </div>
    </div>
  )
}
