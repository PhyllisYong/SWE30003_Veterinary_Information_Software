import { useState, useEffect } from 'react'
import './ContentManagementPage.css'

// ── Types ──────────────────────────────────────────────────────────────
interface ContentItem {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  publicationStatus: string
  content_type: 'guide' | 'video'
  steps?: string[]
  stepCount?: number
  videoURL?: string | null
  durationSec?: number | null
}


// ── Helpers ────────────────────────────────────────────────────────────
const PET_OPTIONS = ['dog', 'cat', 'rabbit', 'hamster', 'guinea_pig']
const CATEGORY_OPTIONS = [
  'bleeding', 'choking', 'fracture', 'heatstroke',
  'cardiac', 'wound', 'poisoning', 'seizure',
]

type UserRole = 'veterinarian' | 'association_admin'

const STATUS_TRANSITIONS: Record<UserRole, Record<string, string[]>> = {
  veterinarian: {
    draft: ['pending_verification'],
    pending_verification: ['verified', 'rejected'],
    verified: [],
    published: [],
    rejected: ['pending_verification'],
  },

  association_admin: {
    draft: ['pending_verification', 'rejected'],
    pending_verification: ['verified', 'rejected'],
    verified: ['published', 'rejected'],
    published: ['rejected'],
    rejected: ['pending_verification'],
  },
}

function capitalise(s: string) {
  return s.replace(/_/g, ' ').charAt(0).toUpperCase() + s.replace(/_/g, ' ').slice(1)
}

function petTagClass(petType: string) {
  const map: Record<string, string> = {
    dog: 'tag tag--pet', cat: 'tag tag--cat',
    rabbit: 'tag tag--rabbit', hamster: 'tag tag--hamster', guinea_pig: 'tag tag--guinea',
  }
  return map[petType] ?? 'tag tag--pet'
}

const EMPTY_FORM = {
  content_type: 'guide' as 'guide' | 'video',
  title: '',
  description: '',
  petType: 'dog',
  emergencyCategory: 'bleeding',
  steps: [''],
  videoURL: '',
  durationSec: '',
}

// ── Component ──────────────────────────────────────────────────────────
export default function ContentManagementPage() {
  // Hardcoded for now — replace with auth context when auth is ready
  const role = localStorage.getItem('userRole') as UserRole
  const userID = localStorage.getItem('userID') // change to 'association_admin' to test admin view
  const token = localStorage.getItem('token')

  const [items, setItems] = useState<ContentItem[]>([])
  const [loadingList, setLoadingList] = useState(true)
  const [listError, setListError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'all' | 'guide' | 'video'>('all')

  const [form, setForm] = useState({
    ...EMPTY_FORM,
  })
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)

  // ── Fetch all content (admin) or own content (vet) ──────────────────
  useEffect(() => {
    setLoadingList(true)

    const endpoint =
      role === 'veterinarian'
        ? '/api/content/mine'
        : '/api/first-aid/search'

    fetch(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((r) => r.json())
      .then((d) => {
        setItems(d.data)
        setLoadingList(false)
      })
      .catch((e: Error) => {
        setListError(e.message)
        setLoadingList(false)
      })
  }, [role, token])

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  // ── Submit new content ───────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!form.title.trim()) return showToast('Title is required.', 'error')

    setSubmitting(true)
    const body =
      form.content_type === 'guide'
        ? {
          content_type: 'guide',
          title: form.title,
          description: form.description || null,
          petType: form.petType,
          emergencyCategory: form.emergencyCategory,

          steps: form.steps.filter((s) => s.trim() !== ''),
        }
        : {
          content_type: 'video',
          title: form.title,
          description: form.description || null,
          petType: form.petType,
          emergencyCategory: form.emergencyCategory,

          videoURL: form.videoURL || null,
          durationSec: form.durationSec ? Number(form.durationSec) : null,
        }

    try {
      const res = await fetch('/api/content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (data.status === 'ok') {
        setItems((prev) => [data.data, ...prev])
        setForm({ ...EMPTY_FORM })
        showToast('Content submitted successfully.', 'success')
      } else {
        showToast(data.message ?? 'Submission failed.', 'error')
      }
    } catch {
      showToast('Network error.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  // ── Status action ────────────────────────────────────────────────────
  const handleStatusChange = async (contentID: string, status: string) => {
    const endpoint =
      status === 'verified' ? `/api/content/${contentID}/verify`
        : status === 'rejected' ? `/api/content/${contentID}/reject`
          : status === 'published' ? `/api/content/${contentID}/publish`
            : null

    const res = await fetch(
      endpoint ?? `/api/content/${contentID}/status`,
      {
        method: endpoint ? 'POST' : 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: endpoint ? undefined : JSON.stringify({ status }),
      }
    )
    const data = await res.json()
    if (data.status === 'ok') {
      setItems((prev) =>
        prev.map((item) =>
          item.contentID === contentID
            ? { ...item, publicationStatus: data.data.publicationStatus }
            : item
        )
      )
      showToast(`Status updated to "${capitalise(status)}".`, 'success')
    } else {
      showToast(data.message ?? 'Update failed.', 'error')
    }
  }

  // ── Delete ───────────────────────────────────────────────────────────
  const handleDelete = async (contentID: string) => {
    if (!confirm('Delete this content? This cannot be undone.')) return
    const res = await fetch(`/api/content/${contentID}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.status === 'ok') {
      setItems((prev) => prev.filter((i) => i.contentID !== contentID))
      showToast('Content deleted.', 'success')
    } else {
      showToast(data.message ?? 'Delete failed.', 'error')
    }
  }

  // ── Steps helpers ────────────────────────────────────────────────────
  const updateStep = (idx: number, val: string) => {
    const steps = [...form.steps]
    steps[idx] = val
    setForm({ ...form, steps })
  }
  const addStep = () => setForm({ ...form, steps: [...form.steps, ''] })
  const removeStep = (idx: number) =>
    setForm({ ...form, steps: form.steps.filter((_, i) => i !== idx) })

  // ── Filtered list ────────────────────────────────────────────────────
  const filtered = items.filter((i) => activeTab === 'all' || i.content_type === activeTab)

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <>
      <div className="cm-header">
        <div className="container">
          <h1>Content Management</h1>
          <p>
            {role === 'veterinarian'
              ? 'Submit new guides and videos. Track the verification status of your submissions.'
              : 'Review, publish, or reject vet-submitted content. Manage all first-aid resources.'}
          </p>
        </div>
      </div>

      <div className="cm-body">
        <div className="container">
          <div className="cm-layout">

            {/* ── LEFT: Submit form (Vet) ── */}
            <div>
              <p className="cm-section-title">Submit New Content</p>
              <div className="cm-form-card">

                {/* Type toggle */}
                <div className="cm-form__group">
                  <label>Content type</label>
                  <select
                    value={form.content_type}
                    onChange={(e) => setForm({ ...form, content_type: e.target.value as 'guide' | 'video' })}
                  >
                    <option value="guide">Guide</option>
                    <option value="video">Video</option>
                  </select>
                </div>

                <div className="cm-form__row">
                  <div className="cm-form__group">
                    <label>Pet type</label>
                    <select value={form.petType} onChange={(e) => setForm({ ...form, petType: e.target.value })}>
                      {PET_OPTIONS.map((p) => <option key={p} value={p}>{capitalise(p)}</option>)}
                    </select>
                  </div>
                  <div className="cm-form__group">
                    <label>Emergency category</label>
                    <select value={form.emergencyCategory} onChange={(e) => setForm({ ...form, emergencyCategory: e.target.value })}>
                      {CATEGORY_OPTIONS.map((c) => <option key={c} value={c}>{capitalise(c)}</option>)}
                    </select>
                  </div>
                </div>

                <div className="cm-form__group">
                  <label>Title</label>
                  <input
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    placeholder="e.g. How to stop bleeding in cats"
                  />
                </div>

                <div className="cm-form__group">
                  <label>Description</label>
                  <textarea
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    placeholder="Brief overview of this content..."
                  />
                </div>

                {/* Guide: steps */}
                {form.content_type === 'guide' && (
                  <div className="cm-form__group">
                    <label>Steps</label>
                    <div className="cm-steps-list">
                      {form.steps.map((step, idx) => (
                        <div key={idx} className="cm-step-item">
                          <span className="cm-step-number">{idx + 1}.</span>
                          <input
                            value={step}
                            onChange={(e) => updateStep(idx, e.target.value)}
                            placeholder={`Step ${idx + 1}`}
                          />
                          {form.steps.length > 1 && (
                            <button className="cm-step-remove" onClick={() => removeStep(idx)}>×</button>
                          )}
                        </div>
                      ))}
                    </div>
                    <button className="cm-add-step" onClick={addStep}>+ Add step</button>
                  </div>
                )}

                {/* Video: URL + duration */}
                {form.content_type === 'video' && (
                  <div className="cm-form__row">
                    <div className="cm-form__group">
                      <label>Video URL</label>
                      <input
                        value={form.videoURL}
                        onChange={(e) => setForm({ ...form, videoURL: e.target.value })}
                        placeholder="https://..."
                      />
                    </div>
                    <div className="cm-form__group">
                      <label>Duration (seconds)</label>
                      <input
                        type="number"
                        value={form.durationSec}
                        onChange={(e) => setForm({ ...form, durationSec: e.target.value })}
                        placeholder="e.g. 180"
                      />
                    </div>
                  </div>
                )}

                <div className="cm-form__actions">
                  <button
                    className="btn btn--primary"
                    onClick={handleSubmit}
                    disabled={submitting}
                  >
                    {submitting ? 'Submitting…' : 'Submit for verification'}
                  </button>
                  <button
                    className="btn btn--secondary"
                    onClick={() => setForm({ ...EMPTY_FORM })}
                  >
                    Clear
                  </button>
                </div>

                {toast && (
                  <div className={`cm-toast cm-toast--${toast.type}`}>{toast.msg}</div>
                )}
              </div>
            </div>

            {/* ── RIGHT: Content list ── */}
            <div>
              <p className="cm-section-title">
                {role === 'veterinarian' ? 'My Submissions' : 'All Content'}
              </p>

              {/* Tabs */}
              <div className="cm-tabs">
                {(['all', 'guide', 'video'] as const).map((t) => (
                  <button
                    key={t}
                    className={`cm-tab${activeTab === t ? ' active' : ''}`}
                    onClick={() => setActiveTab(t)}
                  >
                    {t === 'all' ? 'All' : capitalise(t) + 's'}
                  </button>
                ))}
              </div>

              {loadingList && <div className="cm-empty"><p>Loading content…</p></div>}
              {listError && <div className="cm-empty"><p>Error: {listError}</p></div>}

              {!loadingList && !listError && (
                <div className="cm-list">
                  {filtered.length === 0 ? (
                    <div className="cm-empty"><p>No content found.</p></div>
                  ) : (
                    filtered.map((item) => {
                      const transitions =
                        STATUS_TRANSITIONS[role][item.publicationStatus] ?? []
                      return (
                        <div key={item.contentID} className="cm-list-item">
                          <div className="cm-list-item__top">
                            <span className="cm-list-item__title">{item.title}</span>
                            <span className={`status-badge status-badge--${item.publicationStatus}`}>
                              {capitalise(item.publicationStatus)}
                            </span>
                          </div>

                          <div className="cm-list-item__tags">
                            <span className={petTagClass(item.petType)}>{capitalise(item.petType)}</span>
                            <span className="tag tag--category">{capitalise(item.emergencyCategory)}</span>
                            <span className={`tag tag--${item.content_type}`}>{capitalise(item.content_type)}</span>
                          </div>

                          {item.description && (
                            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 0 }}>
                              {item.description}
                            </p>
                          )}

                          <div className="cm-list-item__actions">
                            {transitions.map((s) => (
                              <button
                                key={s}
                                className={`cm-action-btn ${s === 'rejected' ? 'cm-action-btn--danger' : s === 'published' ? 'cm-action-btn--success' : ''}`}
                                onClick={() => handleStatusChange(item.contentID, s)}
                              >
                                {s === 'pending_verification' ? 'Re-submit'
                                  : s === 'verified' ? 'Verify'
                                    : s === 'published' ? 'Publish'
                                      : s === 'rejected' ? 'Reject'
                                        : capitalise(s)}
                              </button>
                            ))}
                            {role === 'association_admin' && (
                              <button
                                className="cm-action-btn cm-action-btn--danger"
                                onClick={() => handleDelete(item.contentID)}
                              >
                                Delete
                              </button>
                            )}
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </>
  )
}
