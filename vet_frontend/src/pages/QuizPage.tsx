import { useState, useEffect, useRef } from 'react'
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
}

interface QuestionCheck {
  isCorrect: boolean
  correctAnswerID: string | null
}

interface RelatedItem {
  contentID: string
  title: string
  description: string | null
  content_type: string
  emergencyCategory: string
}

// ── Helpers ────────────────────────────────────────────────────────────
function capitalise(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function formatTime(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return m > 0 ? `${m}m ${s}s` : `${s}s`
}

// ── Component ──────────────────────────────────────────────────────────
export default function QuizPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState<QuizDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [phase, setPhase] = useState<'quiz' | 'submitting' | 'results'>('quiz')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selected, setSelected] = useState<Record<string, string>>({})
  const [submittedQuestions, setSubmittedQuestions] = useState<Set<string>>(new Set())
  const [questionChecks, setQuestionChecks] = useState<Record<string, QuestionCheck>>({})
  const [openExplanations, setOpenExplanations] = useState<Set<string>>(new Set())
  const [result, setResult] = useState<SubmitResult | null>(null)
  const [elapsedSec, setElapsedSec] = useState(0)
  const [displaySec, setDisplaySec] = useState(0)
  const [relatedContent, setRelatedContent] = useState<RelatedItem[]>([])

  const startTimeRef = useRef<number>(Date.now())

  useEffect(() => {
    if (!id) return
    fetch(`/api/quizzes/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`)
        return res.json()
      })
      .then((data: QuizDetail) => {
        setQuiz(data)
        startTimeRef.current = Date.now()
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [id])

  useEffect(() => {
    if (phase !== 'quiz') return
    const interval = setInterval(() => {
      setDisplaySec(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [phase])

  const currentQuestion = quiz?.questions[currentIndex] ?? null
  const isCurrentSubmitted = currentQuestion ? submittedQuestions.has(currentQuestion.id) : false
  const selectedForCurrent = currentQuestion ? selected[currentQuestion.id] : undefined

  function handleSelectAnswer(answerId: string) {
    if (!currentQuestion || isCurrentSubmitted) return
    setSelected(prev => ({ ...prev, [currentQuestion.id]: answerId }))
  }

  async function handleSubmitAnswer() {
    if (!currentQuestion || !selectedForCurrent) return

    // Mark as submitted immediately so UI locks
    setSubmittedQuestions(prev => new Set(prev).add(currentQuestion.id))

    // Check the answer against the backend
    try {
      const res = await fetch(`/api/quizzes/${id}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          questionID: currentQuestion.id,
          answerID: selectedForCurrent,
        }),
      })
      if (res.ok) {
        const data: QuestionCheck = await res.json()
        setQuestionChecks(prev => ({ ...prev, [currentQuestion.id]: data }))
      }
    } catch {
      // Non-fatal — correct/incorrect just won't show for this question
    }
  }

  function handleNext() {
    if (!quiz) return
    if (currentIndex < quiz.questions.length - 1) {
      setCurrentIndex(prev => prev + 1)
    } else {
      handleFinalSubmit()
    }
  }

  function toggleExplanation(questionId: string) {
    setOpenExplanations(prev => {
      const next = new Set(prev)
      if (next.has(questionId)) next.delete(questionId)
      else next.add(questionId)
      return next
    })
  }

  async function handleFinalSubmit() {
    if (!quiz) return
    const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000)
    setElapsedSec(elapsed)
    setPhase('submitting')
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
      if (res.status === 401) {
        navigate(`/login?redirect=/quizzes/${id}`, { replace: true })
        return
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let data: any
      try {
        data = await res.json()
      } catch {
        throw new Error(`Server error (${res.status}) — please try again`)
      }
      if (!res.ok) throw new Error((data.detail as string) ?? 'Submission failed')

      const submitResult: SubmitResult = {
        score: data.score as number,
        passed: data.passed as boolean,
        feedback: (data.feedback ?? []) as FeedbackItem[],
      }
      setResult(submitResult)

      // If failed, fetch related content — try category first, fall back to petType only
      if (!data.passed) {
        const petType = quiz.petType
        const category = quiz.emergencyCategory
        const tryFetch = (url: string) =>
          fetch(url).then(r => r.ok ? r.json() : null)

        tryFetch(`/api/first-aid/search?petType=${petType}&category=${category}`)
          .then(d => {
            const items = d?.data ?? []
            if (items.length > 0) return items
            // No category match — fall back to petType only
            return tryFetch(`/api/first-aid/search?petType=${petType}`)
              .then(d2 => d2?.data ?? [])
          })
          .then(items => {
            if (items.length > 0) setRelatedContent(items.slice(0, 3))
          })
          .catch(() => {})
      }

      setPhase('results')
    } catch (err) {
      alert((err as Error).message)
      setPhase('quiz')
    }
  }

  // ── Loading / error ────────────────────────────────────────────────
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

  const totalQuestions = quiz.questions.length
  const isLastQuestion = currentIndex === totalQuestions - 1

  // ── Results screen ─────────────────────────────────────────────────
  if (phase === 'results' && result) {
    const feedbackMap = Object.fromEntries(result.feedback.map(f => [f.questionID, f]))

    return (
      <>
        <div className="quiz-header">
          <div className="container">
            <Link to="/quizzes" className="quiz-header__back">&larr; Back to quizzes</Link>
            <div className="quiz-header__tags">
              <span className="tag tag--pet">{capitalise(quiz.petType)}</span>
              <span className="tag tag--category">{capitalise(quiz.emergencyCategory)}</span>
            </div>
            <h1>{quiz.title}</h1>
          </div>
        </div>

        <div className="quiz-body">
          <div className="container quiz-results-screen">

            {/* Summary card */}
            <div className={`quiz-results-summary ${result.passed ? 'quiz-results-summary--passed' : 'quiz-results-summary--failed'}`}>
              <div className="quiz-results-summary__score">
                {result.score}
                <span className="quiz-results-summary__total">/{quiz.totalScore ?? totalQuestions}</span>
              </div>
              <span className={`quiz-results-badge ${result.passed ? 'passed' : 'failed'}`}>
                {result.passed ? 'Passed' : 'Not passed'}
              </span>
              <div className="quiz-results-summary__time">
                Time taken: <strong>{formatTime(elapsedSec)}</strong>
              </div>
            </div>

            {/* Per-question review */}
            <h2 className="quiz-review-heading">Question Review</h2>
            <div className="quiz-review-list">
              {quiz.questions.map((q, i) => {
                const fb = feedbackMap[q.id]
                const isCorrect = fb?.isCorrect ?? false
                const reviewKey = `review-${q.id}`
                return (
                  <div
                    key={q.id}
                    className={`quiz-review-item ${isCorrect ? 'quiz-review-item--correct' : 'quiz-review-item--incorrect'}`}
                  >
                    <div className="quiz-review-item__header">
                      <span className="quiz-review-item__num">Q{i + 1}</span>
                      <span className="quiz-review-item__text">{q.questionText}</span>
                      <span className={`quiz-review-item__verdict ${isCorrect ? 'correct' : 'incorrect'}`}>
                        {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                      </span>
                    </div>
                    <div className="explanation-accordion explanation-accordion--review">
                      <button
                        className="explanation-accordion__toggle"
                        onClick={() => toggleExplanation(reviewKey)}
                      >
                        <span>Vet Explanation</span>
                        <span className={`explanation-accordion__chevron${openExplanations.has(reviewKey) ? ' open' : ''}`}>▾</span>
                      </button>
                      {openExplanations.has(reviewKey) && (
                        <div className="explanation-accordion__body">
                          {q.explanation
                            ? q.explanation
                            : <em>No explanation provided for this question yet.</em>
                          }
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Related content — only shown on fail */}
            {!result.passed && relatedContent.length > 0 && (
              <div className="quiz-related">
                <h2 className="quiz-review-heading">Recommended Reading</h2>
                <p className="quiz-related__intro">
                  Review these first-aid guides to help you pass next time.
                </p>
                <div className="quiz-related-list">
                  {relatedContent.map(item => (
                    <Link
                      key={item.contentID}
                      to="/first-aid"
                      className="quiz-related-card"
                    >
                      <span className="quiz-related-card__type">
                        {item.content_type === 'video' ? '▶ Video' : '📋 Guide'}
                      </span>
                      <span className="quiz-related-card__title">{item.title}</span>
                      {item.description && (
                        <span className="quiz-related-card__desc">{item.description}</span>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            <Link to="/quizzes" className="btn btn--primary quiz-results-back">
              Back to quizzes
            </Link>
          </div>
        </div>
      </>
    )
  }

  // ── Quiz in progress ───────────────────────────────────────────────
  if (!currentQuestion) return null

  const check = questionChecks[currentQuestion.id]

  return (
    <>
      <div className="quiz-header">
        <div className="container">
          <Link to="/quizzes" className="quiz-header__back">&larr; Back to quizzes</Link>
          <div className="quiz-header__tags">
            <span className="tag tag--pet">{capitalise(quiz.petType)}</span>
            <span className="tag tag--category">{capitalise(quiz.emergencyCategory)}</span>
          </div>
          <h1>{quiz.title}</h1>
          <div className="quiz-header__meta">
            <div className="quiz-header__meta-item">
              <strong>{totalQuestions}</strong> {totalQuestions === 1 ? 'question' : 'questions'}
            </div>
            <div className="quiz-header__meta-item">
              ⏱ <strong>{formatTime(displaySec)}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="quiz-body">
        <div className="container quiz-single-layout">

          {/* Step progress dots */}
          <div className="quiz-step-progress">
            <div className="quiz-step-progress__dots">
              {quiz.questions.map((q, i) => (
                <div
                  key={q.id}
                  className={[
                    'quiz-step-dot',
                    i === currentIndex ? 'quiz-step-dot--active' : '',
                    submittedQuestions.has(q.id)
                      ? (questionChecks[q.id]?.isCorrect ? 'quiz-step-dot--correct' : 'quiz-step-dot--wrong')
                      : i < currentIndex ? 'quiz-step-dot--done' : '',
                  ].filter(Boolean).join(' ')}
                  title={`Question ${i + 1}`}
                />
              ))}
            </div>
            <span className="quiz-step-progress__label">
              {currentIndex + 1} / {totalQuestions}
            </span>
          </div>

          {/* Question card */}
          <div className="question-card question-card--single">
            <div className="question-card__number">
              Question {currentIndex + 1} of {totalQuestions}
            </div>
            <p className="question-card__text">{currentQuestion.questionText}</p>

            <div className="answer-options">
              {currentQuestion.answers.map((answer) => {
                const isSelected = selected[currentQuestion.id] === answer.id
                const isCorrectAnswer = check?.correctAnswerID === answer.id
                const isWrongPick = isSelected && check && !check.isCorrect

                let cls = 'answer-option'
                if (isCurrentSubmitted && check) {
                  if (isCorrectAnswer) cls += ' reveal-correct'
                  else if (isWrongPick) cls += ' reveal-wrong'
                } else if (isSelected) {
                  cls += ' selected'
                }

                return (
                  <button
                    key={answer.id}
                    className={cls}
                    onClick={() => handleSelectAnswer(answer.id)}
                    disabled={isCurrentSubmitted}
                  >
                    <span className="answer-option__indicator">
                      {isCurrentSubmitted && check
                        ? isCorrectAnswer ? '✓' : isWrongPick ? '✗' : ''
                        : ''
                      }
                    </span>
                    {answer.answerText}
                  </button>
                )
              })}
            </div>

            {/* Inline feedback after submit */}
            {isCurrentSubmitted && check && (
              <div className={`question-feedback ${check.isCorrect ? 'question-feedback--correct' : 'question-feedback--wrong'}`}>
                {check.isCorrect ? 'Correct!' : 'Incorrect'}
              </div>
            )}

            {/* Explanation accordion — only after submitting */}
            {isCurrentSubmitted && (
              <div className="explanation-accordion">
                <button
                  className="explanation-accordion__toggle"
                  onClick={() => toggleExplanation(currentQuestion.id)}
                >
                  <span>Vet Explanation</span>
                  <span className={`explanation-accordion__chevron${openExplanations.has(currentQuestion.id) ? ' open' : ''}`}>
                    ▾
                  </span>
                </button>
                {openExplanations.has(currentQuestion.id) && (
                  <div className="explanation-accordion__body">
                    {currentQuestion.explanation
                      ? currentQuestion.explanation
                      : <em>No explanation provided for this question yet.</em>
                    }
                  </div>
                )}
              </div>
            )}

            {/* Action buttons */}
            <div className="question-card__actions">
              {!isCurrentSubmitted ? (
                <button
                  className="btn btn--primary"
                  onClick={handleSubmitAnswer}
                  disabled={!selectedForCurrent}
                >
                  Submit Answer
                </button>
              ) : (
                <button
                  className="btn btn--primary"
                  onClick={handleNext}
                  disabled={phase === 'submitting'}
                >
                  {phase === 'submitting'
                    ? 'Submitting...'
                    : isLastQuestion
                      ? 'Finish Quiz'
                      : 'Next Question →'}
                </button>
              )}
            </div>
          </div>

        </div>
      </div>
    </>
  )
}
