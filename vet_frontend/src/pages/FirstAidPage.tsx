import { useState, useEffect } from 'react'
import './FirstAidPage.css'

// ── Types (adjusted to match backend response) ────────────────────────
interface Guide {
  id: string               // maps to contentID from backend
  title: string
  description: string | null
  petType: string
  category: string
  steps: string[]
  stepCount: number
  // estimatedTime is not in the backend model; we'll compute optionally
}

// ── Constants & Helpers ───────────────────────────────────────────────
const PET_FILTERS = ['all', 'dog', 'cat', 'rabbit', 'hamster', 'guinea pig']

function petTagClass(petType: string): string {
  const map: Record<string, string> = {
    dog: 'tag tag--pet',
    cat: 'tag tag--cat',
    rabbit: 'tag tag--rabbit',
    hamster: 'tag tag--hamster',
    'guinea pig': 'tag tag--guinea',
  }
  return map[petType] ?? 'tag tag--pet'
}

function capitalise(s: string): string {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function formatCategory(cat: string): string {
  const map: Record<string, string> = {
    bleeding: '🩸 Bleeding',
    choking: '🫧 Choking',
    cpr: '❤️ CPR',
    poisoning: '⚠️ Poisoning',
    fracture: '🦴 Fracture',
    heatstroke: '☀️ Heatstroke',
    seizure: '⚡ Seizure',
    wound: '🩹 Wound care',
  }
  return map[cat] ?? capitalise(cat)
}

// Estimate read time: roughly 1 minute per 5 steps (or just a placeholder)
function estimateReadTime(stepCount: number): string {
  if (stepCount <= 0) return '1 min read'
  const minutes = Math.max(1, Math.ceil(stepCount / 5))
  return `${minutes} min read`
}

// ── Modal component (unchanged except prop type uses Guide) ───────────
interface GuideModalProps {
  guide: Guide | null
  onClose: () => void
}

function GuideModal({ guide, onClose }: GuideModalProps) {
  if (!guide) return null

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose()
  }

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEscape)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = ''
    }
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={handleBackdropClick}>
      <div className="modal-container">
        <div className="modal-header">
          <div>
            <h2>{guide.title}</h2>
            <div className="modal-tags">
              <span className={petTagClass(guide.petType)}>
                {capitalise(guide.petType)}
              </span>
              <span className="tag tag--category">
                {formatCategory(guide.category)}
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {guide.description && (
            <div className="modal-description">
              <p>{guide.description}</p>
            </div>
          )}

          <div className="modal-steps">
            <h3>📋 Step-by-step guide</h3>
            <ol>
              {guide.steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="modal-meta">
            <span>⏱️ {estimateReadTime(guide.stepCount)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Main Component: FirstAidPage ───────────────────────────────────────
export default function FirstAidPage() {
  const [guides, setGuides] = useState<Guide[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [activeFilter, setActiveFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedGuide, setSelectedGuide] = useState<Guide | null>(null)

  // Fetch guides from the correct endpoint
  useEffect(() => {
    // Use the search endpoint without filters to get all guides
    fetch('/api/first-aid/search?contentType=guide')
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`)
        return res.json()
      })
      .then((response) => {
        // Expected shape: { status: "ok", data: [...] }
        if (response.status !== 'ok') {
          throw new Error(response.message || 'Unexpected response format')
        }
        // Transform backend fields to frontend Guide interface
        const transformed: Guide[] = response.data.map((item: any) => ({
          id: item.contentID,           // map contentID -> id
          title: item.title,
          description: item.description,
          petType: item.petType,
          category: item.emergencyCategory, // backend field is emergencyCategory
          steps: item.steps || [],
          stepCount: item.stepCount || 0,
        }))
        setGuides(transformed)
        setLoading(false)
      })
      .catch((err: Error) => {
        console.error('Fetch error:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Client-side filtering (pet type + search)
  const filteredGuides = guides.filter((guide) => {
    const matchesPet = activeFilter === 'all' || guide.petType === activeFilter
    if (!matchesPet) return false

    if (!searchTerm.trim()) return true
    const term = searchTerm.toLowerCase()
    return (
      guide.title.toLowerCase().includes(term) ||
      (guide.description && guide.description.toLowerCase().includes(term)) ||
      guide.category.toLowerCase().includes(term)
    )
  })

  const clearSearch = () => setSearchTerm('')
  const handleViewGuide = (guide: Guide) => setSelectedGuide(guide)

  return (
    <>
      <div className="firstaid-header">
        <div className="container">
          <h1>First Aid Guides</h1>
          <p>
            Vet-reviewed emergency procedures and step‑by‑step first aid guides.
            Search by symptom, pet type, or emergency category.
          </p>
        </div>
      </div>

      <div className="firstaid-filters">
        <div className="container firstaid-filters__inner">
          <div className="filter-group">
            <span className="filter-label">Pet type</span>
            {PET_FILTERS.map((f) => (
              <button
                key={f}
                className={`filter-pill${activeFilter === f ? ' active' : ''}`}
                onClick={() => setActiveFilter(f)}
              >
                {f === 'all' ? 'All pets' : capitalise(f)}
              </button>
            ))}
          </div>

          <div className="search-group">
            <input
              type="text"
              className="search-input"
              placeholder="Search by symptom, keyword or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button className="search-clear" onClick={clearSearch}>
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="firstaid-body">
        <div className="container">
          {loading && (
            <div className="guides-empty">
              <p>Loading first aid guides...</p>
            </div>
          )}

          {error && (
            <div className="guides-empty">
              <h3>Could not load guides</h3>
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && (
            <>
              <p className="guides-meta">
                Showing <strong>{filteredGuides.length}</strong>{' '}
                {filteredGuides.length === 1 ? 'guide' : 'guides'}
                {activeFilter !== 'all' && (
                  <> for <strong>{capitalise(activeFilter)}</strong></>
                )}
                {searchTerm && (
                  <> matching "<strong>{searchTerm}</strong>"</>
                )}
              </p>

              <div className="guides-grid">
                {filteredGuides.length === 0 ? (
                  <div className="guides-empty">
                    <h3>No guides found</h3>
                    <p>Try adjusting your pet filter or search term.</p>
                  </div>
                ) : (
                  filteredGuides.map((guide) => (
                    <div key={guide.id} className="guide-card">
                      <div className="guide-card__tags">
                        <span className={petTagClass(guide.petType)}>
                          {capitalise(guide.petType)}
                        </span>
                        <span className="tag tag--category">
                          {formatCategory(guide.category)}
                        </span>
                      </div>

                      <h2>{guide.title}</h2>
                      <p className="guide-card__desc">
                        {guide.description ?? 'Quick reference for emergency care.'}
                      </p>

                      <div className="guide-card__meta">
                        <div className="guide-card__meta-item">
                          <span>{guide.stepCount}</span>{' '}
                          {guide.stepCount === 1 ? 'step' : 'steps'}
                        </div>
                        <div className="guide-card__meta-item">
                          <span>{estimateReadTime(guide.stepCount)}</span> read
                        </div>
                      </div>

                      <div className="guide-card__footer">
                        <button
                          className="btn btn--primary"
                          onClick={() => handleViewGuide(guide)}
                          style={{ width: '100%', justifyContent: 'center' }}
                        >
                          View full guide
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <GuideModal guide={selectedGuide} onClose={() => setSelectedGuide(null)} />
    </>
  )
}
