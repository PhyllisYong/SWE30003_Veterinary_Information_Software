import { useState, useEffect } from 'react'
import './ContentManagementPage.css'

interface ContentItem {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  publicationStatus: string
  content_type: 'guide' | 'video' | 'quiz'
  authorVetID: string | null
  assignedVetID?: string | null 
}

interface VetOption {
  userID: string
  name: string
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

const STATUS_FILTERS = ['all', 'draft', 'pending_verification', 'verified', 'published', 'rejected']

export default function AdminContentPage() {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  const [items, setItems] = useState<ContentItem[]>([])
  const [vets, setVets] = useState<VetOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState<'all' | 'guide' | 'video' | 'quiz'>('all')
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)
  const [assignMap, setAssignMap] = useState<Record<string, string>>({})

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetch('/api/content', { headers }).then(r => r.json()),
      fetch('/api/users?role=veterinarian', { headers }).then(r => r.json()),
    ])
      .then(async ([contentRes, vetsRes]) => {
        const allItems: ContentItem[] = contentRes.data ?? []
        setVets(vetsRes.data ?? [])

        const submitted = allItems.filter(i => i.publicationStatus === 'submitted')
        if (submitted.length > 0) {
          await Promise.all(
            submitted.map(i =>
              fetch(`/api/content/${i.contentID}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify({ status: 'draft' }),
              })
            )
          )
          setItems(allItems.map(i =>
            i.publicationStatus === 'submitted' ? { ...i, publicationStatus: 'draft' } : i
          ))
        } else {
          setItems(allItems)
        }

        setLoading(false)
      })
      .catch((e: Error) => { setError(e.message); setLoading(false) })
  }, [token])

  const handleSetDraft = async (contentID: string) => {
    const reviewerID = assignMap[contentID]
    if (!reviewerID) return showToast('Select a reviewer vet before setting as draft.', 'error')
    const res = await fetch(`/api/content/${contentID}/set-draft`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ assignedVetID: reviewerID }), 
    })
    const data = await res.json()
    if (data.status === 'ok') {
      setItems(prev => prev.map(i => i.contentID === contentID
        ? { ...i, publicationStatus: 'pending_verification', assignedVetID: reviewerID } : i)) 
      showToast('Draft confirmed and reviewer assigned. Status → Pending Verification.', 'success')
    } else { showToast(data.message ?? 'Failed.', 'error') }
  }

  const handlePublish = async (contentID: string) => {
    const res = await fetch(`/api/content/${contentID}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (data.status === 'ok') {
      setItems(prev => prev.map(i => i.contentID === contentID ? { ...i, publicationStatus: 'published' } : i))
      showToast('Content published.', 'success')
    } else { showToast(data.message ?? 'Failed.', 'error') }
  }

  const handleDelete = async (contentID: string) => {
    if (!confirm('Delete this content? This cannot be undone.')) return
    const res = await fetch(`/api/content/${contentID}`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (data.status === 'ok') {
      setItems(prev => prev.filter(i => i.contentID !== contentID))
      showToast('Deleted.', 'success')
    } else { showToast(data.message ?? 'Failed.', 'error') }
  }

  const filtered = items.filter(i =>
    (statusFilter === 'all' || i.publicationStatus === statusFilter) &&
    (typeFilter === 'all' || i.content_type === typeFilter)
  )

  const vetName = (id: string | null | undefined) =>
    vets.find(v => v.userID === id)?.name ?? id ?? '—'

  return (
    <>
      <div className="cm-header">
        <div className="container">
          <h1>Content Management</h1>
          <p>Review all submissions, assign reviewers, publish or request amendments.</p>
        </div>
      </div>

      <div className="cm-admin-filters">
        <div className="container cm-admin-filters__inner">
          <div className="filter-group">
            <span className="filter-label">Status</span>
            {STATUS_FILTERS.map(s => (
              <button key={s} className={`filter-pill${statusFilter === s ? ' active' : ''}`}
                onClick={() => setStatusFilter(s)}>
                {s === 'all' ? 'All' : capitalise(s)}
              </button>
            ))}
          </div>
          <div className="filter-group">
            <span className="filter-label">Type</span>
            {(['all', 'guide', 'video', 'quiz'] as const).map(t => (
              <button key={t} className={`filter-pill${typeFilter === t ? ' active' : ''}`}
                onClick={() => setTypeFilter(t)}>
                {t === 'all' ? 'All' : t === 'quiz' ? 'Quizzes' : capitalise(t) + 's'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="cm-body">
        <div className="container">

          {toast && <div className={`cm-toast cm-toast--${toast.type}`} style={{ marginBottom: 20 }}>{toast.msg}</div>}

          {loading && <div className="cm-empty"><p>Loading content…</p></div>}
          {error && <div className="cm-empty"><p>Error: {error}</p></div>}

          {!loading && !error && (
            <>
              <p className="firstaid-meta" style={{ marginBottom: 16 }}>
                Showing <strong>{filtered.length}</strong> items
              </p>
              <div className="cm-admin-grid">
                {filtered.length === 0
                  ? <div className="cm-empty"><p>No content matches the current filters.</p></div>
                  : filtered.map(item => (
                    <div key={item.contentID} className="cm-list-item cm-admin-card">
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
                        <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 12 }}>
                          {item.description}
                        </p>
                      )}

                      {/* Meta Details Row */}
                      <div className="cm-admin-meta">
                        <span>Author: <strong>{vetName(item.authorVetID)}</strong></span>
                        {item.assignedVetID && (
                          <span>Reviewer: <strong>{vetName(item.assignedVetID)}</strong></span>
                        )}
                      </div>

                      {item.publicationStatus === 'draft' && (
                        <div className="cm-assign-row" style={{ marginTop: 12 }}>
                          <select
                            value={assignMap[item.contentID] ?? item.assignedVetID ?? ''}
                            onChange={e => setAssignMap(prev => ({ ...prev, [item.contentID]: e.target.value }))}
                          >
                            <option value="">
                              {item.assignedVetID 
                                ? `Reassign (current: ${vetName(item.assignedVetID)})` 
                                : 'Assign reviewer…'}
                            </option>
                            {vets.map(v => (
                              <option key={v.userID} value={v.userID}>{v.name}</option>
                            ))}
                          </select>
                          <button className="cm-action-btn" onClick={() => handleSetDraft(item.contentID)}>
                            Confirm &amp; Assign
                          </button>
                        </div>
                      )}

                      <div className="cm-list-item__actions">
                        {/* verified → Publish */}
                        {item.publicationStatus === 'verified' && (
                          <button className="cm-action-btn cm-action-btn--success"
                            onClick={() => handlePublish(item.contentID)}>
                            Publish
                          </button>
                        )}

                        {/* Always: Delete */}
                        <button className="cm-action-btn cm-action-btn--danger"
                          onClick={() => handleDelete(item.contentID)}>
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                }
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
