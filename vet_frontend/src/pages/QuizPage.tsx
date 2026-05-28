import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import './QuizPage.css'

// ── Types ──────────────────────────────────────────────────────────────
interface Answer {
  id: string
  answerText: string
}

interface Question {
  id: string
  questionText: string
  answers: Answer[]
  explanation?: string | null
}

interface FeedbackItem {
  questionID: string
  correctAnswerID: string | null
  submittedAnswerID: string | null
  isCorrect: boolean
}

interface QuizDetail {
  id: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  durationSec: number | null
  totalScore: number | null
  questions: Question[]
}

interface SubmitResult {
  score: number
  passed: boolean
  feedback: FeedbackItem[]
  recommendedContent?: RecommendedContent[]
}

interface RecommendedContent {
  contentID: string
  title: string
  description?: string | null
  petType: string
  emergencyCategory: string
  content_type: 'guide' | 'video' | 'quiz'
}

// ── Helpers ────────────────────────────────────────────────────────────
function capitalise(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function petLabel(petType: string): string {
  return petType
    .replace(/\s+/g, '_')
    .toLowerCase()
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function answerClass(
  answerId: string,
  questionId: string,
  selected: Record<string, string>,
  revealed: Record<string, string> | null, // { answerId: 'correct' | 'incorrect' }
): string {
  const base = 'answer-option'
  const isSelected = selected[questionId] === answerId

  if (!revealed) {
    return isSelected ? `${base} selected` : base
  }

  const verdict = revealed[answerId]
  if (verdict === 'correct' && isSelected) return `${base} correct`
  if (verdict === 'incorrect' && isSelected) return `${base} incorrect`
  if (verdict === 'correct' && !isSelected) return `${base} missed`
  return base
}

// ── Component ──────────────────────────────────────────────────────────
export default function QuizPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState<QuizDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // questionId → answerId
  const [selected, setSelected] = useState<Record<string, string>>({})

  // answerId → 'correct' | 'incorrect' — populated after submit
  const [revealed, setRevealed] = useState<Record<string, string> | null>(null)
  const [result, setResult] = useState<SubmitResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!id) return
    fetch(`/api/quizzes/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`)
        return res.json()
      })
      .then((data: QuizDetail) => {
        setQuiz(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [id])

  function selectAnswer(questionId: string, answerId: string) {
    if (revealed) return // locked after submit
    setSelected((prev) => ({ ...prev, [questionId]: answerId }))
  }

  async function handleSubmit() {
    if (!quiz) return
    setSubmitting(true)
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/quizzes/${id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ answers: selected }),
      })
      const data = await res.json()
      if (res.status === 401) {
        navigate(`/login?redirect=/quizzes/${id}`, { replace: true })
        return
      }
      if (!res.ok) throw new Error(data.detail ?? 'Submission failed')

      // Build a revealed map from the questions + selected answers
      // The server returns the score but not per-answer correctness,
      // so we re-derive it client-side using the explanation field as a hint.
      // For now we mark the selected answers based on whether each question
      // contributed to the score by re-fetching isn't needed — the server
      // already told us total score. We'll reveal via a second lightweight
      // approach: mark selected answers based on score delta isn't possible
      // without per-question feedback. So we request the server send it back.
      setResult({
        score: data.score,
        passed: data.passed,
        feedback: data.feedback ?? [],
        recommendedContent: data.recommendedContent ?? [],
      })

      // Build revealed map: correctAnswerID → 'correct', wrong selected → 'incorrect'
      const revealMap: Record<string, string> = {}
      ;(data.feedback ?? []).forEach((f: FeedbackItem) => {
        if (f.correctAnswerID) revealMap[f.correctAnswerID] = 'correct'
        if (f.submittedAnswerID && !f.isCorrect) revealMap[f.submittedAnswerID] = 'incorrect'
      })
      setRevealed(revealMap)
    } catch (err) {
      alert((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  // ── Render states ────────────────────────────────────────────────────
  if (loading) return (
    <div className="quiz-body">
      <div className="container quiz-state"><p>Loading quiz...</p></div>
    </div>
  )

  if (error || !quiz) return (
    <div className="quiz-body">
      <div className="container quiz-state">
        <h2>Could not load quiz</h2>
        <p>{error}</p>
        <Link to="/quizzes" className="btn btn--outline" style={{ marginTop: 20 }}>
          Back to quizzes
        </Link>
      </div>
    </div>
  )

  const answeredCount = Object.keys(selected).length
  const totalQuestions = quiz.questions.length
  const allAnswered = answeredCount === totalQuestions
  const progressPct = totalQuestions > 0
    ? Math.round((answeredCount / totalQuestions) * 100)
    : 0

  return (
    <>
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="quiz-header">
        <div className="container">
          <Link to="/quizzes" className="quiz-header__back">
            &larr; Back to quizzes
          </Link>

          <div className="quiz-header__tags">
            <span className="tag tag--pet">{petLabel(quiz.petType)}</span>
            <span className="tag tag--category">
              {capitalise(quiz.emergencyCategory)}
            </span>
          </div>

          <h1>{quiz.title}</h1>
          {quiz.description && (
            <p className="quiz-header__desc">{quiz.description}</p>
          )}

          <div className="quiz-header__meta">
            <div className="quiz-header__meta-item">
              <strong>{totalQuestions}</strong>{' '}
              {totalQuestions === 1 ? 'question' : 'questions'}
            </div>
            {quiz.durationSec && (
              <div className="quiz-header__meta-item">
                <strong>{Math.round(quiz.durationSec / 60)} min</strong> suggested
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Body ────────────────────────────────────────────────── */}
      <div className="quiz-body">
        <div className="container">
          <div className="quiz-body__layout">

            {/* Questions */}
            <div className="quiz-questions">
              {quiz.questions.map((question, qIndex) => (
                <div key={question.id} className="question-card">
                  <div className="question-card__number">
                    Question {qIndex + 1} of {totalQuestions}
                  </div>
                  <p className="question-card__text">{question.questionText}</p>

                  <div className="answer-options">
                    {question.answers.map((answer) => (
                      <button
                        key={answer.id}
                        className={answerClass(answer.id, question.id, selected, revealed)}
                        onClick={() => selectAnswer(question.id, answer.id)}
                        disabled={!!revealed}
                      >
                        <span className="answer-option__indicator">
                          {selected[question.id] === answer.id && !revealed && '•'}
                        </span>
                        {answer.answerText}
                      </button>
                    ))}
                  </div>

                  {/* Show explanation after submission */}
                  {result && question.explanation && (
                    <div className="question-card__explanation">
                      <strong>💡 Explanation</strong>
                      {question.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Sidebar */}
            <aside className="quiz-sidebar">

              {/* Progress */}
              <div className="quiz-progress-card">
                <h3>Your progress</h3>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
                <p className="progress-label">
                  {answeredCount} of {totalQuestions} answered
                </p>

                <div className="quiz-dot-grid">
                  {quiz.questions.map((q, i) => (
                    <div
                      key={q.id}
                      className={`quiz-dot${selected[q.id] ? ' answered' : ''}`}
                      title={`Question ${i + 1}`}
                    >
                      {i + 1}
                    </div>
                  ))}
                </div>
              </div>

              {/* Result card (shown after submit) */}
              {result && (
                <div className="quiz-result-card">
                  <div className="quiz-result-card__score">{result.score}</div>
                  <div className="quiz-result-card__total">
                    out of {quiz.totalScore ?? totalQuestions}
                  </div>
                  <span className={`quiz-result-card__badge ${result.passed ? 'passed' : 'failed'}`}>
                    {result.passed ? 'Passed' : 'Not passed'}
                  </span>
                </div>
              )}

              {result && !result.passed && (result.recommendedContent?.length ?? 0) > 0 && (
                <div className="quiz-recommend-card">
                  <h3>Recommended review</h3>
                  {result.recommendedContent?.map(item => (
                    <Link
                      key={item.contentID}
                      to={item.content_type === 'video' ? '/videos' : '/guides'}
                      className="quiz-recommend-item"
                    >
                      <span>{item.content_type === 'video' ? 'Video' : 'Guide'}</span>
                      <strong>{item.title}</strong>
                    </Link>
                  ))}
                </div>
              )}

              {/* Submit */}
              {!result && (
                <button
                  className="btn btn--primary quiz-submit-btn"
                  onClick={handleSubmit}
                  disabled={!allAnswered || submitting}
                >
                  {submitting
                    ? 'Submitting...'
                    : allAnswered
                      ? 'Submit quiz'
                      : `Answer all questions to submit`}
                </button>
              )}

              {result && (
                <Link to="/quizzes" className="btn btn--outline quiz-submit-btn">
                  Back to quizzes
                </Link>
              )}

            </aside>
          </div>
        </div>
      </div>
    </>
  )
}
