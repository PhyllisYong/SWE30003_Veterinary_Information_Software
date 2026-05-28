import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './VetQuizManagePage.css'

// ── Types ──────────────────────────────────────────────────────────────────────

interface QuizSummary {
  id: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  questionCount: number
}

interface Answer {
  id: string
  answerText: string
}

interface Question {
  id: string
  questionText: string
  answers: Answer[]
  explanation?: string
}

interface QuizDetail {
  id: string
  title: string
  questions: Question[]
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

// ── Component ──────────────────────────────────────────────────────────────────

export default function VetQuizManagePage() {
  const navigate = useNavigate()

  const [quizzes, setQuizzes]         = useState<QuizSummary[]>([])
  const [activeQuiz, setActiveQuiz]   = useState<QuizDetail | null>(null)
  const [explanations, setExplanations] = useState<Record<string, string>>({})
  const [saving, setSaving]           = useState<Record<string, boolean>>({})
  const [saved, setSaved]             = useState<Record<string, boolean>>({})
  const [pageError, setPageError]     = useState<string | null>(null)

  // ── Auth guard (vet only) ────────────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('token')
    const role  = localStorage.getItem('userRole')
    if (!token || role !== 'veterinarian') {
      navigate('/login')
      return
    }
    fetch('/api/quizzes')
      .then(r => r.json())
      .then((data: QuizSummary[]) => setQuizzes(data))
      .catch(() => setPageError('Failed to load quizzes.'))
  }, [navigate])

  // ── Open quiz → load questions ───────────────────────────────────────────────
  const openQuiz = async (quizID: string) => {
    setPageError(null)
    try {
      const res        = await apiFetch(`/api/quizzes/${quizID}`)
      const data: QuizDetail = await res.json()
      setActiveQuiz(data)
      const init: Record<string, string> = {}
      data.questions.forEach(q => { init[q.id] = q.explanation ?? '' })
      setExplanations(init)
      setSaved({})
    } catch {
      setPageError('Failed to load quiz.')
    }
  }

  // ── Save explanation for one question ────────────────────────────────────────
  const saveExplanation = async (questionID: string) => {
    if (!activeQuiz) return
    setSaving(prev => ({ ...prev, [questionID]: true }))
    try {
      const res = await apiFetch(
        `/api/quizzes/${activeQuiz.id}/questions/${questionID}/explanation`,
        {
          method: 'PUT',
          body:   JSON.stringify({ explanation: explanations[questionID] ?? '' }),
        }
      )
      if (res.ok) {
        setSaved(prev => ({ ...prev, [questionID]: true }))
        setTimeout(() => setSaved(prev => ({ ...prev, [questionID]: false })), 2000)
      } else {
        const body = await res.json()
        setPageError(body.detail ?? 'Save failed.')
      }
    } catch {
      setPageError('Could not reach server.')
    } finally {
      setSaving(prev => ({ ...prev, [questionID]: false }))
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="vqm-page">
      <h1>Quiz Explanations</h1>
      <p className="vqm-subtitle">
        Select a quiz to add or edit per-question clinical explanations.
      </p>

      {pageError && <p className="vqm-error">{pageError}</p>}

      <div className="vqm-layout">

        {/* ── Quiz sidebar ─────────────────────────────────────────────── */}
        <aside className="vqm-sidebar">
          {quizzes.length === 0 ? (
            <p className="vqm-empty">No published quizzes.</p>
          ) : (
            <ul className="vqm-quiz-list">
              {quizzes.map(q => (
                <li
                  key={q.id}
                  className={`vqm-quiz-item${activeQuiz?.id === q.id ? ' vqm-quiz-item--active' : ''}`}
                  onClick={() => openQuiz(q.id)}
                >
                  <span className="vqm-quiz-item__title">{q.title}</span>
                  <span className="vqm-quiz-item__meta">
                    {q.petType} · {q.emergencyCategory} · {q.questionCount}Q
                  </span>
                </li>
              ))}
            </ul>
          )}
        </aside>

        {/* ── Question panel ───────────────────────────────────────────── */}
        <main className="vqm-main">
          {!activeQuiz ? (
            <div className="vqm-placeholder">
              <span>📋</span>
              <p>Select a quiz from the left to edit explanations.</p>
            </div>
          ) : (
            <>
              <h2>{activeQuiz.title}</h2>
              <div className="vqm-questions">
                {activeQuiz.questions.map((q, idx) => (
                  <div key={q.id} className="vqm-question">
                    <p className="vqm-question__text">
                      <strong>Q{idx + 1}.</strong> {q.questionText}
                    </p>
                    <ul className="vqm-answers">
                      {q.answers.map(a => (
                        <li key={a.id}>{a.answerText}</li>
                      ))}
                    </ul>
                    <label className="vqm-label" htmlFor={`exp-${q.id}`}>
                      Explanation
                    </label>
                    <textarea
                      id={`exp-${q.id}`}
                      className="vqm-textarea"
                      rows={3}
                      placeholder="Provide a clinical explanation for this question…"
                      value={explanations[q.id] ?? ''}
                      onChange={e =>
                        setExplanations(prev => ({ ...prev, [q.id]: e.target.value }))
                      }
                    />
                    <div className="vqm-question__footer">
                      {saved[q.id] && <span className="vqm-saved">✓ Saved</span>}
                      <button
                        className="btn btn--primary btn--sm"
                        disabled={saving[q.id]}
                        onClick={() => saveExplanation(q.id)}
                      >
                        {saving[q.id] ? 'Saving…' : 'Save'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </main>

      </div>
    </div>
  )
}
