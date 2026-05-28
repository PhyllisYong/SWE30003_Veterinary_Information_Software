import { useState, useEffect } from 'react'
import './ContentManagementPage.css'

// ── Types ──────────────────────────────────────────────────────────────
interface Vet {
  userID: string
  name: string
}

interface ContentItem {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  publicationStatus: string
  content_type: 'guide' | 'video'
  authorVetID: string | null
  steps?: string[]
  stepCount?: number
  videoURL?: string | null
  durationSec?: number | null
  assignedVetID?: string | null
}

type UserRole = 'veterinarian' | 'association_admin'

// ── Helpers ────────────────────────────────────────────────────────────
const PET_OPTIONS = ['dog', 'cat', 'rabbit', 'hamster', 'guinea_pig']
const CATEGORY_OPTIONS = [
  'bleeding', 'choking', 'fracture', 'heatstroke',
  'cardiac', 'wound', 'poisoning', 'seizure',
]

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
  const role = localStorage.getItem('userRole') as UserRole
  const token = localStorage.getItem('token')

  // My submissions (vet) or all content (admin)
  const [myItems, setMyItems] = useState<ContentItem[]>([])
  // Other vets' pending content (vet review section)
  const [assignedItems, setAssignedItems] = useState<ContentItem[]>([])

  const [loadingList, setLoadingList] = useState(true)
  const [listError, setListError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'all' | 'guide' | 'video'>('all')
  const [reviewTab, setReviewTab] = useState<'all' | 'guide' | 'video'>('all')

  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)

  // comment per contentID for review section
  const [comments, setComments] = useState<Record<string, string>>({})
  const [vets, setVets] = useState<Vet[]>([])

  // ── Fetch ────────────────────────────────────────────────────────────
  useEffect(() => {
    setLoadingList(true)
    const headers = { Authorization: `Bearer ${token}` }

    if (role === 'veterinarian') {
      Promise.all([
        fetch('/api/content/mine', { headers }).then(r => r.json()),
        fetch('/api/content/assigned', { headers }).then(r => r.json()),
      ])
        .then(([mine, assigned]) => {
          setMyItems(mine.data ?? [])
          setAssignedItems(assigned.data ?? [])
          setLoadingList(false)
        })
        .catch((e: Error) => { setListError(e.message); setLoadingList(false) })
    } else {
      // Admin: all content + vet list for assignment
      Promise.all([
        fetch('/api/content', { headers }).then(r => r.json()),
        fetch('/api/content/vets', { headers }).then(r => r.json()),
      ])
        .then(([content, vetList]) => {
          setMyItems(content.data ?? [])
          setVets(vetList.data ?? [])
          setLoadingList(false)
        })
        .catch((e: Error) => { setListError(e.message); setLoadingList(false) })
    }
  }, [role, token])

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }
  const handleAssignVet = async (contentID: string, vetID: string) => {
    const res = await fetch(`/api/content/${contentID}/assign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ vetID }),
    })

    const data = await res.json()

    if (data.status === 'ok') {
      setMyItems(prev =>
        prev.map(item =>
          item.contentID === contentID
            ? { ...item, assignedVetID: vetID, publicationStatus: 'pending_verification' }
            : item
        )
      )
    }
  }

  // ── Submit new content ───────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!form.title.trim()) return showToast('Title is required.', 'error')
    setSubmitting(true)
    const body =
      form.content_type === 'guide'
        ? {
          content_type: 'guide', title: form.title,
          description: form.description || null,
          petType: form.petType, emergencyCategory: form.emergencyCategory,
          steps: form.steps.filter((s) => s.trim() !== ''),
        }
        : {
          content_type: 'video', title: form.title,
          description: form.description || null,
          petType: form.petType, emergencyCategory: form.emergencyCategory,
          videoURL: form.videoURL || null,
          durationSec: form.durationSec ? Number(form.durationSec) : null,
        }
    try {
      const res = await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (data.status === 'ok') {
        setMyItems((prev) => [data.data, ...prev])
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

  // ── Status change (shared) ───────────────────────────────────────────
  const callStatusAPI = async (contentID: string, status: string) => {
    const endpoint =
      status === 'verified' ? `/api/content/${contentID}/verify`
        : status === 'rejected' ? `/api/content/${contentID}/reject`
          : status === 'published' ? `/api/content/${contentID}/publish`
            : null
    return fetch(endpoint ?? `/api/content/${contentID}/status`, {
      method: endpoint ? 'POST' : 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: endpoint ? undefined : JSON.stringify({ status }),
    }).then((r) => r.json())
  }

  // Vet: resubmit own rejected content
  const handleResubmit = async (contentID: string) => {
    const data = await callStatusAPI(contentID, 'pending_verification')
    if (data.status === 'ok') {
      setMyItems((prev) =>
        prev.map((item) =>
          item.contentID === contentID
            ? { ...item, publicationStatus: 'pending_verification' }
            : item
        )
      )
      showToast('Re-submitted for verification.', 'success')
    } else {
      showToast(data.message ?? 'Failed.', 'error')
    }
  }

  // Vet: verify or reject another vet's content (with comment)
  const handleReview = async (contentID: string, status: 'verified' | 'rejected') => {
    const comment = comments[contentID]?.trim()
    if (status === 'rejected' && !comment) {
      return showToast('Please add a comment before rejecting.', 'error')
    }
    // TODO: send comment to backend when comment API is ready
    const data = await callStatusAPI(contentID, status)
    if (data.status === 'ok') {
      setAssignedItems((prev) => prev.filter((i) => i.contentID !== contentID))
      showToast(`Content ${status === 'verified' ? 'verified' : 'rejected'}.`, 'success')
    } else {
      showToast(data.message ?? 'Failed.', 'error')
    }
  }

  // Admin: any status change
  const handleAdminStatusChange = async (contentID: string, status: string) => {
    const data = await callStatusAPI(contentID, status)
    if (data.status === 'ok') {
      setMyItems((prev) =>
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

  // Admin: delete
  const handleDelete = async (contentID: string) => {
    if (!confirm('Delete this content? This cannot be undone.')) return
    const res = await fetch(`/api/content/${contentID}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (data.status === 'ok') {
      setMyItems((prev) => prev.filter((i) => i.contentID !== contentID))
      showToast('Content deleted.', 'success')
    } else {
      showToast(data.message ?? 'Delete failed.', 'error')
    }
  }

  // ── Steps helpers ────────────────────────────────────────────────────
  const updateStep = (idx: number, val: string) => {
    const steps = [...form.steps]; steps[idx] = val; setForm({ ...form, steps })
  }
  const addStep = () => setForm({ ...form, steps: [...form.steps, ''] })
  const removeStep = (idx: number) =>
    setForm({ ...form, steps: form.steps.filter((_, i) => i !== idx) })

  // ── Filtered lists ───────────────────────────────────────────────────
  const filteredMine = myItems.filter((i) => activeTab === 'all' || i.content_type === activeTab)
  const filteredReview = assignedItems.filter(
  (i) => reviewTab === 'all' || i.content_type === reviewTab
)

  const ADMIN_TRANSITIONS: Record<string, string[]> = {
    draft: ['pending_verification', 'rejected'],
    pending_verification: ['verified', 'rejected'],
    verified: ['published', 'rejected'],
    published: ['rejected'],
    rejected: ['pending_verification'],
  }

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <>
      <div className="cm-header">
        <div className="container">
          <h1>Content Management</h1>
          <p>
            {role === 'veterinarian'
              ? 'Submit guides and videos, track your submissions, and review pending content from other vets.'
              : 'Review, publish, or reject vet-submitted content. Manage all first-aid resources.'}
          </p>
        </div>
      </div>

      <div className="cm-body">
        <div className="container">
          <div className={`cm-layout${role === 'association_admin' ? ' cm-layout--full' : ''}`}>

            {/* ── LEFT: Submit form (vet only) ── */}
            {role === 'veterinarian' && <div>
              <p className="cm-section-title">Submit New Content</p>
              <div className="cm-form-card">
                <div className="cm-form__group">
                  <label>Content type</label>
                  <select value={form.content_type} onChange={(e) => setForm({ ...form, content_type: e.target.value as 'guide' | 'video' })}>
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
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. How to stop bleeding in cats" />
                </div>
                <div className="cm-form__group">
                  <label>Description</label>
                  <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief overview of this content..." />
                </div>
                {form.content_type === 'guide' && (
                  <div className="cm-form__group">
                    <label>Steps</label>
                    <div className="cm-steps-list">
                      {form.steps.map((step, idx) => (
                        <div key={idx} className="cm-step-item">
                          <span className="cm-step-number">{idx + 1}.</span>
                          <input value={step} onChange={(e) => updateStep(idx, e.target.value)} placeholder={`Step ${idx + 1}`} />
                          {form.steps.length > 1 && (
                            <button className="cm-step-remove" onClick={() => removeStep(idx)}>×</button>
                          )}
                        </div>
                      ))}
                    </div>
                    <button className="cm-add-step" onClick={addStep}>+ Add step</button>
                  </div>
                )}
                {form.content_type === 'video' && (
                  <div className="cm-form__row">
                    <div className="cm-form__group">
                      <label>Video URL</label>
                      <input value={form.videoURL} onChange={(e) => setForm({ ...form, videoURL: e.target.value })} placeholder="https://..." />
                    </div>
                    <div className="cm-form__group">
                      <label>Duration (seconds)</label>
                      <input type="number" value={form.durationSec} onChange={(e) => setForm({ ...form, durationSec: e.target.value })} placeholder="e.g. 180" />
                    </div>
                  </div>
                )}
                <div className="cm-form__actions">
                  <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
                    {submitting ? 'Submitting…' : 'Submit for verification'}
                  </button>
                  <button className="btn btn--secondary" onClick={() => setForm({ ...EMPTY_FORM })}>Clear</button>
                </div>
                {toast && <div className={`cm-toast cm-toast--${toast.type}`}>{toast.msg}</div>}
              </div>
            </div>}

            {/* ── RIGHT: Lists ── */}
            <div className="cm-right-col">

              {/* ── My Submissions ── */}
              <p className="cm-section-title">
                {role === 'veterinarian' ? 'My Submissions' : 'All Content'}
              </p>
              <div className="cm-tabs">
                {(['all', 'guide', 'video'] as const).map((t) => (
                  <button key={t} className={`cm-tab${activeTab === t ? ' active' : ''}`} onClick={() => setActiveTab(t)}>
                    {t === 'all' ? 'All' : capitalise(t) + 's'}
                  </button>
                ))}
              </div>

              {loadingList && <div className="cm-empty"><p>Loading content…</p></div>}
              {listError && <div className="cm-empty"><p>Error: {listError}</p></div>}

              {!loadingList && !listError && (
                <div className="cm-list">
                  {filteredMine.length === 0
                    ? <div className="cm-empty"><p>No content found.</p></div>
                    : filteredMine.map((item) => (
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
                          {/* Vet: only resubmit if rejected */}
                          {role === 'veterinarian' && item.publicationStatus === 'rejected' && (
                            <button className="cm-action-btn" onClick={() => handleResubmit(item.contentID)}>
                              Re-submit
                            </button>
                          )}
                          {/* Admin: full transitions */}
                          {role === 'association_admin' && (
                            <div className="cm-form__group">
                              <label>Assign Vet to Verify</label>
                              <select
                                value={item.assignedVetID ?? ''}
                                onChange={(e) => handleAssignVet(item.contentID, e.target.value)}
                              >
                                <option value="">— select a vet —</option>
                                {vets.map((v) => (
                                  <option key={v.userID} value={v.userID}>{v.name}</option>
                                ))}
                              </select>
                            </div>
                          )}
                          {role === 'association_admin' && (
                            <>

                              {(ADMIN_TRANSITIONS[item.publicationStatus] ?? []).map((s) => (
                                <button
                                  key={s}
                                  className={`cm-action-btn ${s === 'rejected' ? 'cm-action-btn--danger' : s === 'published' ? 'cm-action-btn--success' : ''}`}
                                  onClick={() => handleAdminStatusChange(item.contentID, s)}
                                >
                                  {s === 'pending_verification' ? 'Re-submit'
                                    : s === 'verified' ? 'Verify'
                                      : s === 'published' ? 'Publish'
                                        : s === 'rejected' ? 'Reject'
                                          : capitalise(s)}
                                </button>
                              ))}
                              <button className="cm-action-btn cm-action-btn--danger" onClick={() => handleDelete(item.contentID)}>
                                Delete
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    ))
                  }
                </div>
              )}

              {/* ── Review Others (Vet only) ── */}
              {role === 'veterinarian' && (
                <>
                  <div className="cm-review-divider" />
                  <p className="cm-section-title">
                    Review Pending Content
                    {filteredReview.length > 0 && (
                      <span className="cm-review-badge">{filteredReview.length}</span>
                    )}
                  </p>
                  <p className="cm-review-hint">
                    Content submitted by other vets awaiting peer review. You cannot review your own submissions.
                  </p>

                  <div className="cm-tabs">
                    {(['all', 'guide', 'video'] as const).map((t) => (
                      <button key={t} className={`cm-tab${reviewTab === t ? ' active' : ''}`} onClick={() => setReviewTab(t)}>
                        {t === 'all' ? 'All' : capitalise(t) + 's'}
                      </button>
                    ))}
                  </div>

                  {filteredReview.length === 0
                    ? <div className="cm-empty"><p>No pending content to review.</p></div>
                    : (
                      <div className="cm-list">
                        {filteredReview.map((item) => (
                          <div key={item.contentID} className="cm-list-item cm-list-item--review">
                            <div className="cm-list-item__top">
                              <span className="cm-list-item__title">{item.title}</span>
                              <span className="status-badge status-badge--pending_verification">Pending</span>
                            </div>
                            <div className="cm-list-item__tags">
                              <span className={petTagClass(item.petType)}>{capitalise(item.petType)}</span>
                              <span className="tag tag--category">{capitalise(item.emergencyCategory)}</span>
                              <span className={`tag tag--${item.content_type}`}>{capitalise(item.content_type)}</span>
                            </div>
                            {item.description && (
                              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 12 }}>
                                {item.description}
                              </p>
                            )}

                            {/* Comment box */}
                            <div className="cm-form__group" style={{ marginBottom: 12 }}>
                              <label>Comment <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>(required for rejection)</span></label>
                              <textarea
                                rows={2}
                                placeholder="Add feedback or notes for the author…"
                                value={comments[item.contentID] ?? ''}
                                onChange={(e) => setComments((prev) => ({ ...prev, [item.contentID]: e.target.value }))}
                              />
                            </div>

                            <div className="cm-list-item__actions">
                              <button className="cm-action-btn cm-action-btn--success" onClick={() => handleReview(item.contentID, 'verified')}>
                                Verify
                              </button>
                              <button className="cm-action-btn cm-action-btn--danger" onClick={() => handleReview(item.contentID, 'rejected')}>
                                Reject
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )
                  }
                </>
              )}

            </div>
          </div>
        </div>
      </div>
    </>
  )
}
