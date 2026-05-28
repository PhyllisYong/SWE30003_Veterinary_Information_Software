import { useState, useEffect } from 'react'
import './VideoPage.css'

// ── Types ──────────────────────────────────────────────────────────────
interface Video {
  id: string               // contentID
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  videoURL: string
  durationSec: number | null
}

// ── Constants & Helpers ───────────────────────────────────────────────
const PET_FILTERS = ['all', 'dog', 'cat', 'rabbit', 'hamster', 'guinea_pig']

function normalizePetType(petType: string): string {
  return petType.replace(/\s+/g, '_').toLowerCase()
}

function petLabel(petType: string): string {
  return normalizePetType(petType)
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function petTagClass(petType: string): string {
  const map: Record<string, string> = {
    dog: 'tag tag--pet',
    cat: 'tag tag--cat',
    rabbit: 'tag tag--rabbit',
    hamster: 'tag tag--hamster',
    guinea_pig: 'tag tag--guinea',
  }
  return map[normalizePetType(petType)] ?? 'tag tag--pet'
}

function capitalise(s: string): string {
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

function formatDuration(sec: number | null): string {
  if (!sec) return '—'
  const mins = Math.floor(sec / 60)
  const remainingSec = sec % 60
  if (mins === 0) return `${sec}s`
  if (remainingSec === 0) return `${mins} min`
  return `${mins} min ${remainingSec}s`
}

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

// Extract YouTube video ID to build thumbnail without an API key.
function getYouTubeThumbnail(url: string): string | null {
  const videoId = getYouTubeVideoId(url)
  if (!videoId) return null
  return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
}

// ── Modal Component (Video Player) ────────────────────────────────────
interface VideoModalProps {
  video: Video | null
  onClose: () => void
}

function VideoModal({ video, onClose }: VideoModalProps) {
  if (!video) return null

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

  const embedUrl = getEmbedUrl(video.videoURL)

  return (
    <div className="modal-overlay" onClick={handleBackdropClick}>
      <div className="modal-container modal-video">
        <div className="modal-header">
          <div>
            <h2>{video.title}</h2>
            <div className="modal-tags">
              <span className={petTagClass(video.petType)}>
                {petLabel(video.petType)}
              </span>
              <span className="tag tag--category">
                {formatCategory(video.emergencyCategory)}
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div className="video-wrapper">
            <iframe
              src={embedUrl}
              title={video.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
          {video.description && (
            <div className="modal-description">
              <p>{video.description}</p>
            </div>
          )}
          <div className="modal-meta">
            <span>⏱️ {formatDuration(video.durationSec)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Main Component: VideoPage ─────────────────────────────────────────
export default function VideoPage() {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [activeFilter, setActiveFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)

  useEffect(() => {
    // Use your existing search endpoint, but filter for video content_type
    // Adjust URL as needed – e.g., /api/first-aid/search?contentType=video
    fetch('/api/first-aid/search?contentType=video')
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text()
          throw new Error(`Server ${res.status}: ${text.substring(0, 150)}`)
        }
        return res.json()
      })
      .then((response) => {
        if (response.status !== 'ok') {
          throw new Error(response.message || 'Unexpected response')
        }
        // Filter only video items (content_type === 'video')
        const videoItems = response.data.filter((item: any) => item.content_type === 'video')
        const transformed: Video[] = videoItems.map((item: any) => ({
          id: item.contentID,
          title: item.title,
          description: item.description,
          petType: item.petType,
          emergencyCategory: item.emergencyCategory,
          videoURL: item.videoURL,
          durationSec: item.durationSec,
        }))
        setVideos(transformed)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Filtering by pet type and search term
  const filteredVideos = videos.filter((video) => {
    const matchesPet = activeFilter === 'all' || normalizePetType(video.petType) === activeFilter
    if (!matchesPet) return false

    if (!searchTerm.trim()) return true
    const term = searchTerm.toLowerCase()
    return (
      video.title.toLowerCase().includes(term) ||
      (video.description && video.description.toLowerCase().includes(term)) ||
      video.emergencyCategory.toLowerCase().includes(term)
    )
  })

  const clearSearch = () => setSearchTerm('')

  return (
    <>
      <div className="video-header">
        <div className="container">
          <h1>Video Library</h1>
          <p>
            Watch expert-led videos on pet first aid techniques, step‑by‑step
            demonstrations, and emergency preparedness.
          </p>
        </div>
      </div>

      <div className="video-filters">
        <div className="container video-filters__inner">
          <div className="filter-group">
            <span className="filter-label">Pet type</span>
            {PET_FILTERS.map((f) => (
              <button
                key={f}
                className={`filter-pill${activeFilter === f ? ' active' : ''}`}
                onClick={() => setActiveFilter(f)}
              >
                {f === 'all' ? 'All pets' : petLabel(f)}
              </button>
            ))}
          </div>
          <div className="search-group">
            <input
              type="text"
              className="search-input"
              placeholder="Search by title, category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button className="search-clear" onClick={clearSearch}>✕</button>
            )}
          </div>
        </div>
      </div>

      <div className="video-body">
        <div className="container">
          {loading && (
            <div className="videos-empty">
              <p>Loading videos...</p>
            </div>
          )}

          {error && (
            <div className="videos-empty">
              <h3>Could not load videos</h3>
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && (
            <>
              <p className="videos-meta">
                Showing <strong>{filteredVideos.length}</strong>{' '}
                {filteredVideos.length === 1 ? 'video' : 'videos'}
                {activeFilter !== 'all' && (
                  <> for <strong>{petLabel(activeFilter)}</strong></>
                )}
                {searchTerm && <> matching "<strong>{searchTerm}</strong>"</>}
              </p>

              <div className="videos-grid">
                {filteredVideos.length === 0 ? (
                  <div className="videos-empty">
                    <h3>No videos found</h3>
                    <p>Try adjusting your filters or search term.</p>
                  </div>
                ) : (
                  filteredVideos.map((video) => (
                    <div key={video.id} className="video-card">
                      <div
                        className="video-card__thumbnail"
                        onClick={() => setSelectedVideo(video)}
                        style={
                          getYouTubeThumbnail(video.videoURL)
                            ? {
                                backgroundImage: `url(${getYouTubeThumbnail(video.videoURL)})`,
                                backgroundSize: 'cover',
                                backgroundPosition: 'center',
                              }
                            : { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
                        }
                      >
                        <div className="play-icon">▶</div>
                      </div>

                      <div className="video-card__content">
                        <div className="video-card__tags">
                          <span className={petTagClass(video.petType)}>
                            {petLabel(video.petType)}
                          </span>
                          <span className="tag tag--category">
                            {formatCategory(video.emergencyCategory)}
                          </span>
                        </div>
                        <h2>{video.title}</h2>
                        <p className="video-card__desc">
                          {video.description ?? 'Watch this video to learn essential first aid skills.'}
                        </p>
                        <div className="video-card__meta">
                          <div className="video-card__meta-item">
                            <span>{formatDuration(video.durationSec)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <VideoModal video={selectedVideo} onClose={() => setSelectedVideo(null)} />
    </>
  )
}
