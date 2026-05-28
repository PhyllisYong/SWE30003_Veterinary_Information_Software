import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './QuizListPage.css'

// ── Types ──────────────────────────────────────────────────────────────
interface Quiz {
  id: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  questionCount: number
  durationSec: number | null
}

// ── Helpers ────────────────────────────────────────────────────────────
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

function formatDuration(sec: number | null): string {
  if (!sec) return '—'
  if (sec < 60) return `${sec}s`
  return `${Math.round(sec / 60)} min`
}

function capitalise(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

// ── Component ──────────────────────────────────────────────────────────
export default function QuizListPage() {
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState('all')

  useEffect(() => {
    fetch('/api/quizzes')
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`)
        return res.json()
      })
      .then((data: Quiz[]) => {
        setQuizzes(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const filtered =
    activeFilter === 'all'
      ? quizzes
      : quizzes.filter((q) => normalizePetType(q.petType) === activeFilter)

  return (
    <>
      {/* Page header */}
      <div className="quiz-list-header">
        <div className="container">
          <h1>Knowledge Quizzes</h1>
          <p>
            Vet-reviewed quizzes to test your first-aid knowledge.
            Filter by pet type and work through each category at your own pace.
          </p>
        </div>
      </div>

      {/* Sticky filter bar */}
      <div className="quiz-list-filters">
        <div className="container quiz-list-filters__inner">
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
      </div>

      {/* Body */}
      <div className="quiz-list-body">
        <div className="container">

          {/* Loading */}
          {loading && (
            <div className="quiz-empty">
              <p>Loading quizzes...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="quiz-empty">
              <h3>Could not load quizzes</h3>
              <p>{error}</p>
            </div>
          )}

          {/* Results */}
          {!loading && !error && (
            <>
              <p className="quiz-list-meta">
                Showing <strong>{filtered.length}</strong>{' '}
                {filtered.length === 1 ? 'quiz' : 'quizzes'}
                {activeFilter !== 'all' && (
                  <> for <strong>{petLabel(activeFilter)}</strong></>
                )}
              </p>

              <div className="quiz-grid">
                {filtered.length === 0 ? (
                  <div className="quiz-empty">
                    <h3>No quizzes found</h3>
                    <p>Try selecting a different pet type.</p>
                  </div>
                ) : (
                  filtered.map((quiz) => (
                    <div key={quiz.id} className="quiz-card">
                      <div className="quiz-card__tags">
                        <span className={petTagClass(quiz.petType)}>
                          {petLabel(quiz.petType)}
                        </span>
                        <span className="tag tag--category">
                          {capitalise(quiz.emergencyCategory)}
                        </span>
                      </div>

                      <h2>{quiz.title}</h2>
                      <p className="quiz-card__desc">
                        {quiz.description ?? 'No description provided.'}
                      </p>

                      <div className="quiz-card__meta">
                        <div className="quiz-card__meta-item">
                          <span>{quiz.questionCount}</span>{' '}
                          {quiz.questionCount === 1 ? 'question' : 'questions'}
                        </div>
                        <div className="quiz-card__meta-item">
                          <span>{formatDuration(quiz.durationSec)}</span> duration
                        </div>
                      </div>

                      <div className="quiz-card__footer">
                        <Link
                          to={`/quizzes/${quiz.id}`}
                          className="btn btn--primary"
                          style={{ width: '100%', justifyContent: 'center' }}
                        >
                          Start quiz
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

        </div>
      </div>
    </>
  )
}
