import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import './GuidesPage.css'

// ── Types ──────────────────────────────────────────────────────────────────────
interface GuideResult {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  content_type: string
  steps: string[]
  stepCount: number
}

interface VideoResult {
  contentID: string
  title: string
  videoURL: string | null
  durationSec: number | null
}

interface SearchResponse {
  status: 'ok' | 'warning'
  data: (GuideResult & VideoResult)[]
  message?: string
}

// ── Static data ────────────────────────────────────────────────────────────────
const PET_TYPES = [
  { value: 'dog',        label: 'Dog',        emoji: '🐕' },
  { value: 'cat',        label: 'Cat',        emoji: '🐈' },
  { value: 'rabbit',     label: 'Rabbit',     emoji: '🐇' },
  { value: 'hamster',    label: 'Hamster',    emoji: '🐹' },
  { value: 'guinea_pig', label: 'Guinea Pig', emoji: '🐾' },
]

const EMERGENCIES = [
  { value: 'choking',           label: 'Choking',           emoji: '🫁' },
  { value: 'bleeding',          label: 'Bleeding',          emoji: '🩸' },
  { value: 'poisoning',         label: 'Poisoning',         emoji: '☠️' },
  { value: 'fracture',          label: 'Fracture',          emoji: '🦴' },
  { value: 'burns',             label: 'Burns',             emoji: '🔥' },
  { value: 'breathing',         label: 'Breathing',         emoji: '😮‍💨' },
  { value: 'seizure',           label: 'Seizure',           emoji: '⚡' },
  { value: 'heatstroke',        label: 'Heatstroke',        emoji: '🌡️' },
  { value: 'unconscious',       label: 'Unconscious',       emoji: '😵' },
  { value: 'allergic_reaction', label: 'Allergic Reaction', emoji: '🤧' },
]

function petEmoji(value: string) {
  return PET_TYPES.find(p => p.value === value)?.emoji ?? '🐾'
}

function petLabel(value: string) {
  return PET_TYPES.find(p => p.value === value)?.label ?? value
}

function emergencyEmoji(value: string) {
  return EMERGENCIES.find(e => e.value === value)?.emoji ?? '⚠️'
}

function emergencyLabel(value: string) {
  return EMERGENCIES.find(e => e.value === value)?.label
    ?? value.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

// ── Guide modal ────────────────────────────────────────────────────────────────
function GuideModal({
  guide,
  onClose,
}: {
  guide: GuideResult
  onClose: () => void
}) {
  const [video, setVideo]   = useState<VideoResult | null>(null)
  const [vidLoading, setVidLoading] = useState(true)
  const backdropRef = useRef<HTMLDivElement>(null)

  // Fetch associated video (same pet + category)
  useEffect(() => {
    const params = new URLSearchParams({
      contentType: 'video',
      petType: guide.petType,
      category: guide.emergencyCategory,
    })
    fetch(`/api/first-aid/search?${params}`)
      .then(r => r.json())
      .then((body: SearchResponse) => {
        const vid = body.data?.[0] ?? null
        setVideo(vid?.videoURL ? (vid as unknown as VideoResult) : null)
      })
      .catch(() => setVideo(null))
      .finally(() => setVidLoading(false))
  }, [guide.contentID])

  // Close on ESC
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  function handleBackdropClick(e: React.MouseEvent) {
    if (e.target === backdropRef.current) onClose()
  }

  return (
    <div className="guide-modal-backdrop" ref={backdropRef} onClick={handleBackdropClick}>
      <div className="guide-modal" role="dialog" aria-modal="true">

        {/* Header */}
        <div className="guide-modal__header">
          <div className="guide-modal__title-area">
            <h2 className="guide-modal__title">{guide.title}</h2>
            <div className="guide-modal__tags">
              <span className="guide-tag guide-tag--pet">
                {petEmoji(guide.petType)} {petLabel(guide.petType)}
              </span>
              <span className="guide-tag guide-tag--emergency">
                {emergencyEmoji(guide.emergencyCategory)} {emergencyLabel(guide.emergencyCategory)}
              </span>
            </div>
          </div>
          <button className="guide-modal__close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* Scrollable body */}
        <div className="guide-modal__body">
          {guide.description && (
            <p className="guide-modal__desc">{guide.description}</p>
          )}

          {/* Steps */}
          {guide.steps.length > 0 ? (
            <ol className="guide-steps guide-steps--modal">
              {guide.steps.map((step, i) => (
                <li key={i} className="guide-step">
                  <span className="guide-step__num">{i + 1}</span>
                  <span className="guide-step__text">{step}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="guide-card__no-steps">No steps available yet.</p>
          )}

          {/* Associated video */}
          <div className="guide-modal__video-section">
            <h3 className="guide-modal__video-title">Associated Video</h3>
            {vidLoading ? (
              <div className="guides-state guides-state--compact">
                <div className="guides-spinner" />
              </div>
            ) : video ? (
              <div className="guide-modal__video-wrap">
                <iframe
                  src={getEmbedUrl(video.videoURL!)}
                  title={video.title}
                  allowFullScreen
                  className="guide-modal__iframe"
                />
              </div>
            ) : (
              <p className="guide-modal__no-video">
                No video available for this guide.{' '}
                <Link to="/vet-advice" onClick={onClose}>Ask a vet</Link> for more help.
              </p>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

// ── Guide card list ────────────────────────────────────────────────────────────
function GuideCards({
  guides,
  onSelect,
}: {
  guides: GuideResult[]
  onSelect: (guide: GuideResult) => void
}) {
  return (
    <div className="guide-list">
      {guides.map(guide => (
        <button
          key={guide.contentID}
          className="guide-card guide-card--clickable"
          onClick={() => onSelect(guide)}
        >
          <div className="guide-card__titles">
            <span className="guide-card__title">{guide.title}</span>
            {guide.description && (
              <span className="guide-card__desc">{guide.description}</span>
            )}
          </div>
          <div className="guide-card__footer">
            <div className="guide-card__tags">
              <span className="guide-tag guide-tag--pet">
                {petEmoji(guide.petType)} {petLabel(guide.petType)}
              </span>
              <span className="guide-tag guide-tag--emergency">
                {emergencyEmoji(guide.emergencyCategory)} {emergencyLabel(guide.emergencyCategory)}
              </span>
            </div>
            <span className="guide-card__cta">View guide →</span>
          </div>
        </button>
      ))}
    </div>
  )
}

// ── Page component ─────────────────────────────────────────────────────────────
function getYouTubeVideoId(url: string): string | null {
  return (
    url.match(/youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/)?.[1] ??
    url.match(/youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/)?.[1] ??
    url.match(/youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/)?.[1] ??
    url.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/)?.[1] ??
    null
  )
}

function getEmbedUrl(url: string): string {
  const videoId = getYouTubeVideoId(url)
  return videoId ? `https://www.youtube.com/embed/${videoId}` : url
}

export default function GuidesPage() {
  const [mode, setMode] = useState<'browse' | 'emergency'>('browse')
  const [selectedGuide, setSelectedGuide] = useState<GuideResult | null>(null)

  // Browse state
  const [allGuides, setAllGuides]             = useState<GuideResult[]>([])
  const [browseLoading, setBrowseLoading]     = useState(true)
  const [petFilter, setPetFilter]             = useState<string | null>(null)
  const [browseSearch, setBrowseSearch]       = useState('')
  const [searchResults, setSearchResults]     = useState<GuideResult[] | null>(null)
  const [searchLoading, setSearchLoading]     = useState(false)

  // Emergency state
  const [petType, setPetType]     = useState<string | null>(null)
  const [category, setCategory]   = useState<string | null>(null)
  const [otherDesc, setOtherDesc] = useState('')
  const [useOther, setUseOther]   = useState(false)
  const [results, setResults]     = useState<GuideResult[] | null>(null)
  const [warningMsg, setWarningMsg] = useState<string | null>(null)
  const [loading, setLoading]     = useState(false)

  // Load all guides on mount
  useEffect(() => {
    fetch('/api/first-aid/search?contentType=guide')
      .then(r => r.json())
      .then((body: SearchResponse) => setAllGuides(body.data as unknown as GuideResult[]))
      .catch(() => setAllGuides([]))
      .finally(() => setBrowseLoading(false))
  }, [])

  // Auto-search in emergency mode
  useEffect(() => {
    if (mode === 'emergency' && petType && category && !useOther) {
      runSearch(petType, category, null)
    }
  }, [petType, category, useOther, mode])

  // Browse: debounced fuzzy search via backend
  useEffect(() => {
    const query = browseSearch.trim()
    if (!query) {
      setSearchResults(null)
      setSearchLoading(false)
      return
    }
    setSearchLoading(true)
    const timer = setTimeout(() => {
      const params = new URLSearchParams({ contentType: 'guide', otherDesc: query })
      if (petFilter) params.set('petType', petFilter)
      fetch(`/api/first-aid/search?${params}`)
        .then(r => r.json())
        .then((body: SearchResponse) => setSearchResults(body.data as unknown as GuideResult[]))
        .catch(() => setSearchResults([]))
        .finally(() => setSearchLoading(false))
    }, 300)
    return () => clearTimeout(timer)
  }, [browseSearch, petFilter])

  // Browse: pet filter applied on top of fuzzy results (or all guides when no search)
  const displayedGuides = (searchResults ?? allGuides).filter(
    g => !petFilter || g.petType === petFilter
  )

  async function runSearch(pet: string, cat: string | null, desc: string | null) {
    setLoading(true)
    setResults(null)
    setWarningMsg(null)

    const params = new URLSearchParams({ contentType: 'guide' })
    if (pet)  params.set('petType', pet)
    if (cat)  params.set('category', cat)
    if (desc) params.set('otherDesc', desc)

    try {
      const res = await fetch(`/api/first-aid/search?${params}`)
      const body: SearchResponse = await res.json()
      setResults(body.data as unknown as GuideResult[])
      if (body.status === 'warning') setWarningMsg(body.message ?? null)
    } catch {
      setWarningMsg('Could not reach the server. Please try again.')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  function handleOtherSubmit(e: { preventDefault(): void }) {
    e.preventDefault()
    if (!petType || !otherDesc.trim()) return
    runSearch(petType, null, otherDesc.trim())
  }

  function selectPet(value: string) {
    setPetType(value)
    setCategory(null)
    setResults(null)
    setWarningMsg(null)
    setUseOther(false)
    setOtherDesc('')
  }

  function selectCategory(value: string) {
    setUseOther(false)
    setOtherDesc('')
    setCategory(value)
  }

  function toggleOther() {
    setUseOther(prev => !prev)
    setCategory(null)
    setResults(null)
    setWarningMsg(null)
  }

  function enterEmergency() {
    setMode('emergency')
    setPetType(null)
    setCategory(null)
    setResults(null)
    setWarningMsg(null)
    setUseOther(false)
    setOtherDesc('')
  }

  // ── Browse mode ──────────────────────────────────────────────────────────────
  if (mode === 'browse') {
    return (
      <div className="guides-page">
        {selectedGuide && (
          <GuideModal guide={selectedGuide} onClose={() => setSelectedGuide(null)} />
        )}

        <div className="guides-hero">
          <h1>First Aid Guides</h1>
          <p>Browse pet emergency guides or get instant step-by-step help.</p>
        </div>

        <div className="guides-content container">

          <div className="emergency-banner">
            <div className="emergency-banner__body">
              <span className="emergency-banner__icon">🚨</span>
              <div>
                <strong>Is this an emergency?</strong>
                <p>Get guided step-by-step first aid instantly.</p>
              </div>
            </div>
            <button className="emergency-banner__btn" onClick={enterEmergency}>
              Emergency Mode
            </button>
          </div>

          <div className="filter-chips">
            <button
              className={`filter-chip${!petFilter ? ' filter-chip--active' : ''}`}
              onClick={() => setPetFilter(null)}
            >
              All
            </button>
            {PET_TYPES.map(p => (
              <button
                key={p.value}
                className={`filter-chip${petFilter === p.value ? ' filter-chip--active' : ''}`}
                onClick={() => setPetFilter(petFilter === p.value ? null : p.value)}
              >
                {p.emoji} {p.label}
              </button>
            ))}
          </div>

          <input
            className="browse-search"
            type="text"
            placeholder="Search guides…"
            value={browseSearch}
            onChange={e => setBrowseSearch(e.target.value)}
          />

          {browseLoading || searchLoading ? (
            <div className="guides-state">
              <div className="guides-spinner" />
              <p>{browseLoading ? 'Loading guides…' : 'Searching…'}</p>
            </div>
          ) : displayedGuides.length === 0 ? (
            <div className="guides-state">
              <p>No guides found. Try a different filter or search term.</p>
            </div>
          ) : (
            <GuideCards guides={displayedGuides} onSelect={setSelectedGuide} />
          )}

        </div>
      </div>
    )
  }

  // ── Emergency mode ───────────────────────────────────────────────────────────
  return (
    <div className="guides-page">
      {selectedGuide && (
        <GuideModal guide={selectedGuide} onClose={() => setSelectedGuide(null)} />
      )}

      <div className="guides-hero guides-hero--emergency">
        <h1>🚨 Emergency Mode</h1>
        <p>Select your pet and the emergency to get step-by-step guidance fast.</p>
      </div>

      <div className="guides-content container">

        <button className="guides-back-btn" onClick={() => setMode('browse')}>
          ← Back to Browse
        </button>

        <section className="guides-section">
          <h2 className="guides-section__title">
            <span className="guides-step">1</span> Select your pet
          </h2>
          <div className="pet-grid">
            {PET_TYPES.map(p => (
              <button
                key={p.value}
                className={`pet-btn${petType === p.value ? ' selected' : ''}`}
                onClick={() => selectPet(p.value)}
              >
                <span className="pet-btn__emoji">{p.emoji}</span>
                <span className="pet-btn__label">{p.label}</span>
              </button>
            ))}
          </div>
        </section>

        {petType && (
          <section className="guides-section">
            <h2 className="guides-section__title">
              <span className="guides-step">2</span> What's happening?
            </h2>

            <div className="emergency-grid">
              {EMERGENCIES.map(e => (
                <button
                  key={e.value}
                  className={`emergency-btn${category === e.value && !useOther ? ' selected' : ''}`}
                  onClick={() => selectCategory(e.value)}
                >
                  <span className="emergency-btn__emoji">{e.emoji}</span>
                  <span className="emergency-btn__label">{e.label}</span>
                </button>
              ))}
              <button
                className={`emergency-btn emergency-btn--other${useOther ? ' selected' : ''}`}
                onClick={toggleOther}
              >
                <span className="emergency-btn__emoji">🔍</span>
                <span className="emergency-btn__label">Not sure…</span>
              </button>
            </div>

            {useOther && (
              <form className="other-form" onSubmit={handleOtherSubmit}>
                <input
                  type="text"
                  className="other-form__input"
                  placeholder="Describe what you're seeing, e.g. 'vomiting after eating chocolate'"
                  value={otherDesc}
                  onChange={e => setOtherDesc(e.target.value)}
                  autoFocus
                />
                <button
                  type="submit"
                  className="btn btn--primary other-form__btn"
                  disabled={!otherDesc.trim() || loading}
                >
                  Search
                </button>
              </form>
            )}
          </section>
        )}

        {loading && (
          <div className="guides-state">
            <div className="guides-spinner" />
            <p>Finding guides…</p>
          </div>
        )}

        {!loading && warningMsg && (
          <div className="guides-warning">
            <span className="guides-warning__icon">⚠️</span>
            <div>
              <p className="guides-warning__text">{warningMsg}</p>
              <Link to="/vet-advice" className="btn btn--primary guides-warning__cta">
                Open Vet Advice Chat
              </Link>
            </div>
          </div>
        )}

        {!loading && results && results.length > 0 && (
          <section className="guides-section">
            <h2 className="guides-section__title">
              <span className="guides-step">✓</span>
              {results.length} guide{results.length !== 1 ? 's' : ''} found
            </h2>
            <GuideCards guides={results} onSelect={setSelectedGuide} />
          </section>
        )}

      </div>
    </div>
  )
}
