import { useState, useEffect } from 'react'
import './ContentManagementPage.css'

interface QuizAnswer {
  answerID?: string
  answerText: string
  isCorrect: boolean
}

interface QuizQuestion {
  questionID?: string
  questionText: string
  answers: QuizAnswer[]
}

interface ContentItem {
  contentID: string
  title: string
  description: string | null
  petType: string
  emergencyCategory: string
  publicationStatus: string
  content_type: 'guide' | 'video' | 'quiz'
  authorVetID: string | null
  steps?: string[]
  stepCount?: number
  videoURL?: string | null
  durationSec?: number | null
  reviewComment?: string | null
  questionCount?: number
  questions?: QuizQuestion[]
}

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

const EMPTY_QUIZ_QUESTION = (): QuizQuestion => ({
  questionText: '',
  answers: [
    { answerText: '', isCorrect: true },
    { answerText: '', isCorrect: false },
  ],
})

const EMPTY_FORM = {
  content_type: 'guide' as 'guide' | 'video' | 'quiz',
  title: '', description: '',
  petType: 'dog', emergencyCategory: 'bleeding',
  steps: [''], videoURL: '', durationSec: '',
  questions: [EMPTY_QUIZ_QUESTION()] as QuizQuestion[],
}

export default function VetContentPage() {
  const token  = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  const [myItems,     setMyItems]     = useState<ContentItem[]>([])
  const [assigned,    setAssigned]    = useState<ContentItem[]>([])
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState<string | null>(null)
  const [activeTab,   setActiveTab]   = useState<'all'|'guide'|'video'|'quiz'>('all')
  const [reviewTab,   setReviewTab]   = useState<'all'|'guide'|'video'|'quiz'>('all')
  const [form,        setForm]        = useState({ ...EMPTY_FORM })
  const [submitting,  setSubmitting]  = useState(false)
  const [toast,       setToast]       = useState<{msg:string;type:'success'|'error'}|null>(null)
  const [comments,    setComments]    = useState<Record<string,string>>({})
  // editing an existing item
  const [editingID,   setEditingID]   = useState<string|null>(null)

  const showToast = (msg: string, type: 'success'|'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetch('/api/content/mine',            { headers }).then(r => r.json()),
      fetch('/api/content/assigned', { headers }).then(r => r.json()),
    ])
      .then(([mine, assignedRes]) => {
        setMyItems(mine.data ?? [])
        setAssigned(assignedRes.data ?? [])
        setLoading(false)
      })
      .catch((e: Error) => { setError(e.message); setLoading(false) })
  }, [token])

  // ── Submit / update ──────────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!form.title.trim()) return showToast('Title is required.', 'error')
    setSubmitting(true)
    if (form.content_type === 'quiz') {
      if (form.questions.length === 0) return showToast('Add at least one question.', 'error')
      for (const q of form.questions) {
        if (!q.questionText.trim()) return showToast('All questions must have text.', 'error')
        if (q.answers.filter(a => a.answerText.trim()).length < 2) return showToast('Each question needs at least 2 answers.', 'error')
        if (!q.answers.some(a => a.isCorrect)) return showToast('Each question must have a correct answer marked.', 'error')
      }
    }
    const base = { title: form.title, description: form.description || null, petType: form.petType, emergencyCategory: form.emergencyCategory }
    const body = form.content_type === 'guide'
      ? { ...base, content_type: 'guide', steps: form.steps.filter(s => s.trim() !== '') }
      : form.content_type === 'video'
      ? { ...base, content_type: 'video', videoURL: form.videoURL || null, durationSec: form.durationSec ? Number(form.durationSec) : null }
      : { ...base, content_type: 'quiz', durationSec: form.durationSec ? Number(form.durationSec) : null,
          questions: form.questions.map(q => ({ questionText: q.questionText, answers: q.answers.filter(a => a.answerText.trim()) })) }
    try {
      const isEdit = editingID !== null
      const res = await fetch(isEdit ? `/api/content/${editingID}` : '/api/content', {
        method: isEdit ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (data.status === 'ok') {
        if (isEdit) {
          setMyItems(prev => prev.map(i => i.contentID === editingID ? data.data : i))
          setEditingID(null)
          showToast('Content updated.', 'success')
        } else {
          setMyItems(prev => [data.data, ...prev])
          showToast('Submitted for review.', 'success')
        }
        setForm({ ...EMPTY_FORM })
      } else {
        showToast(data.message ?? 'Failed.', 'error')
      }
    } catch { showToast('Network error.', 'error') }
    finally { setSubmitting(false) }
  }

  const startEdit = (item: ContentItem) => {
    setEditingID(item.contentID)
    setForm({
      content_type: item.content_type,
      title: item.title,
      description: item.description ?? '',
      petType: item.petType,
      emergencyCategory: item.emergencyCategory,
      steps: item.steps?.length ? item.steps : [''],
      videoURL: item.videoURL ?? '',
      durationSec: item.durationSec?.toString() ?? '',
      questions: item.questions?.length
        ? item.questions.map(q => ({ questionText: q.questionText, answers: q.answers.map(a => ({ answerText: a.answerText, isCorrect: a.isCorrect })) }))
        : [EMPTY_QUIZ_QUESTION()],
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const cancelEdit = () => { setEditingID(null); setForm({ ...EMPTY_FORM }) }

  // ── Review: verify / reject assigned content ─────────────────────────
  const handleReview = async (contentID: string, status: 'verified'|'rejected') => {
    const comment = comments[contentID]?.trim()
    if (status === 'rejected' && !comment)
      return showToast('A comment is required before rejecting.', 'error')

    const res = await fetch(`/api/content/${contentID}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status, comment: comment ?? '' }),
    })
    const data = await res.json()
    if (data.status === 'ok') {
      setAssigned(prev => prev.filter(i => i.contentID !== contentID))
      showToast(`Content ${status === 'verified' ? 'verified' : 'rejected'}.`, 'success')
    } else {
      showToast(data.message ?? 'Failed.', 'error')
    }
  }

  const filteredMine   = myItems.filter(i => activeTab === 'all' || i.content_type === activeTab)
  const filteredAssign = assigned.filter(i => reviewTab === 'all' || i.content_type === reviewTab)

  const updateStep = (idx: number, val: string) => {
    const steps = [...form.steps]; steps[idx] = val; setForm({ ...form, steps })
  }

  const updateQuestion = (qIdx: number, text: string) => {
    const questions = form.questions.map((q, i) => i === qIdx ? { ...q, questionText: text } : q)
    setForm({ ...form, questions })
  }
  const addQuestion = () => setForm({ ...form, questions: [...form.questions, EMPTY_QUIZ_QUESTION()] })
  const removeQuestion = (qIdx: number) => setForm({ ...form, questions: form.questions.filter((_, i) => i !== qIdx) })
  const updateAnswer = (qIdx: number, aIdx: number, text: string) => {
    const questions = form.questions.map((q, i) => i !== qIdx ? q : {
      ...q, answers: q.answers.map((a, j) => j === aIdx ? { ...a, answerText: text } : a),
    })
    setForm({ ...form, questions })
  }
  const setCorrectAnswer = (qIdx: number, aIdx: number) => {
    const questions = form.questions.map((q, i) => i !== qIdx ? q : {
      ...q, answers: q.answers.map((a, j) => ({ ...a, isCorrect: j === aIdx })),
    })
    setForm({ ...form, questions })
  }
  const addAnswer = (qIdx: number) => {
    const questions = form.questions.map((q, i) => i !== qIdx ? q : {
      ...q, answers: [...q.answers, { answerText: '', isCorrect: false }],
    })
    setForm({ ...form, questions })
  }
  const removeAnswer = (qIdx: number, aIdx: number) => {
    const questions = form.questions.map((q, i) => i !== qIdx ? q : {
      ...q, answers: q.answers.filter((_, j) => j !== aIdx),
    })
    setForm({ ...form, questions })
  }

  return (
    <>
      <div className="cm-header">
        <div className="container">
          <h1>My Content</h1>
          <p>Submit first-aid guides and videos, track your submission status, and review content assigned to you.</p>
        </div>
      </div>

      <div className="cm-body">
        <div className="container">
          <div className="cm-layout">

            {/* ── LEFT: Submit / Edit form ── */}
            <div>
              <p className="cm-section-title">
                {editingID ? 'Edit Content' : 'Submit New Content'}
              </p>
              <div className="cm-form-card">
                <div className="cm-form__group">
                  <label>Content type</label>
                  <select value={form.content_type} disabled={!!editingID}
                    onChange={e => setForm({ ...form, content_type: e.target.value as 'guide'|'video'|'quiz' })}>
                    <option value="guide">Guide</option>
                    <option value="video">Video</option>
                    <option value="quiz">Quiz</option>
                  </select>
                </div>
                <div className="cm-form__row">
                  <div className="cm-form__group">
                    <label>Pet type</label>
                    <select value={form.petType} onChange={e => setForm({ ...form, petType: e.target.value })}>
                      {PET_OPTIONS.map(p => <option key={p} value={p}>{capitalise(p)}</option>)}
                    </select>
                  </div>
                  <div className="cm-form__group">
                    <label>Emergency category</label>
                    <select value={form.emergencyCategory} onChange={e => setForm({ ...form, emergencyCategory: e.target.value })}>
                      {CATEGORY_OPTIONS.map(c => <option key={c} value={c}>{capitalise(c)}</option>)}
                    </select>
                  </div>
                </div>
                <div className="cm-form__group">
                  <label>Title</label>
                  <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                    placeholder="e.g. How to stop bleeding in cats" />
                </div>
                <div className="cm-form__group">
                  <label>Description</label>
                  <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                    placeholder="Brief overview..." />
                </div>
                {form.content_type === 'guide' && (
                  <div className="cm-form__group">
                    <label>Steps</label>
                    <div className="cm-steps-list">
                      {form.steps.map((step, idx) => (
                        <div key={idx} className="cm-step-item">
                          <span className="cm-step-number">{idx + 1}.</span>
                          <input value={step} onChange={e => updateStep(idx, e.target.value)}
                            placeholder={`Step ${idx + 1}`} />
                          {form.steps.length > 1 && (
                            <button className="cm-step-remove"
                              onClick={() => setForm({ ...form, steps: form.steps.filter((_, i) => i !== idx) })}>×</button>
                          )}
                        </div>
                      ))}
                    </div>
                    <button className="cm-add-step"
                      onClick={() => setForm({ ...form, steps: [...form.steps, ''] })}>+ Add step</button>
                  </div>
                )}
                {form.content_type === 'video' && (
                  <div className="cm-form__row">
                    <div className="cm-form__group">
                      <label>Video URL</label>
                      <input value={form.videoURL} onChange={e => setForm({ ...form, videoURL: e.target.value })}
                        placeholder="https://youtube.com/..." />
                    </div>
                    <div className="cm-form__group">
                      <label>Duration (seconds)</label>
                      <input type="number" value={form.durationSec}
                        onChange={e => setForm({ ...form, durationSec: e.target.value })} placeholder="e.g. 180" />
                    </div>
                  </div>
                )}
                {form.content_type === 'quiz' && (
                  <>
                    <div className="cm-form__group">
                      <label>Duration (seconds)</label>
                      <input type="number" value={form.durationSec}
                        onChange={e => setForm({ ...form, durationSec: e.target.value })} placeholder="e.g. 300" />
                    </div>
                    <div className="cm-form__group">
                      <label>Questions ({form.questions.length})</label>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {form.questions.map((q, qIdx) => (
                          <div key={qIdx} style={{ border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}>
                            <div className="cm-step-item" style={{ marginBottom: 10 }}>
                              <span className="cm-step-number">{qIdx + 1}.</span>
                              <input value={q.questionText}
                                onChange={e => updateQuestion(qIdx, e.target.value)}
                                placeholder="Question text" />
                              {form.questions.length > 1 && (
                                <button className="cm-step-remove" onClick={() => removeQuestion(qIdx)}>×</button>
                              )}
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, paddingLeft: 20 }}>
                              {q.answers.map((a, aIdx) => (
                                <div key={aIdx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                  <input type="radio" name={`correct-${qIdx}`} checked={a.isCorrect}
                                    onChange={() => setCorrectAnswer(qIdx, aIdx)}
                                    title="Mark as correct" />
                                  <input value={a.answerText}
                                    onChange={e => updateAnswer(qIdx, aIdx, e.target.value)}
                                    placeholder={`Answer ${aIdx + 1}`}
                                    style={{ flex: 1 }} />
                                  {q.answers.length > 2 && (
                                    <button className="cm-step-remove" onClick={() => removeAnswer(qIdx, aIdx)}>×</button>
                                  )}
                                </div>
                              ))}
                            </div>
                            {q.answers.length < 4 && (
                              <button className="cm-add-step" style={{ marginTop: 8 }}
                                onClick={() => addAnswer(qIdx)}>+ Add answer</button>
                            )}
                          </div>
                        ))}
                      </div>
                      <button className="cm-add-step" style={{ marginTop: 12 }}
                        onClick={addQuestion}>+ Add question</button>
                    </div>
                  </>
                )}
                <div className="cm-form__actions">
                  <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
                    {submitting ? 'Saving…' : editingID ? 'Save changes' : 'Submit for review'}
                  </button>
                  {editingID
                    ? <button className="btn btn--secondary" onClick={cancelEdit}>Cancel</button>
                    : <button className="btn btn--secondary" onClick={() => setForm({ ...EMPTY_FORM })}>Clear</button>
                  }
                </div>
                {toast && <div className={`cm-toast cm-toast--${toast.type}`}>{toast.msg}</div>}
              </div>
            </div>

            {/* ── RIGHT ── */}
            <div className="cm-right-col">

              {/* My Submissions */}
              <p className="cm-section-title">My Submissions</p>
              <div className="cm-tabs">
                {(['all','guide','video','quiz'] as const).map(t => (
                  <button key={t} className={`cm-tab${activeTab===t?' active':''}`} onClick={() => setActiveTab(t)}>
                    {t === 'all' ? 'All' : capitalise(t)+'s'}
                  </button>
                ))}
              </div>

              {loading && <div className="cm-empty"><p>Loading…</p></div>}
              {error   && <div className="cm-empty"><p>Error: {error}</p></div>}

              {!loading && !error && (
                <div className="cm-list">
                  {filteredMine.length === 0
                    ? <div className="cm-empty"><p>No submissions yet.</p></div>
                    : filteredMine.map(item => (
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
                          <p style={{ fontSize:13, color:'var(--text-muted)', lineHeight:1.5, marginBottom:0 }}>
                            {item.description}
                          </p>
                        )}
                        {item.content_type === 'quiz' && item.questionCount !== undefined && (
                          <p style={{ fontSize:12, color:'var(--text-muted)', marginTop:4, marginBottom:0 }}>
                            {item.questionCount} question{item.questionCount !== 1 ? 's' : ''}
                          </p>
                        )}
                        {item.reviewComment && (
                          <div className="cm-amend-feedback">
                            <span className="cm-amend-label">Reviewer comment:</span> {item.reviewComment}
                          </div>
                        )}
                        <div className="cm-list-item__actions">
                          {(item.publicationStatus === 'submitted' || item.publicationStatus === 'rejected') && (
                            <button className="cm-action-btn" onClick={() => startEdit(item)}>Edit</button>
                          )}
                        </div>
                      </div>
                    ))
                  }
                </div>
              )}

            </div>
          </div>

          {/* Assigned for Review — full width below the two-column layout */}
          <div className="cm-review-divider" />
              <p className="cm-section-title">
                Assigned for Review
                {filteredAssign.length > 0 && (
                  <span className="cm-review-badge">{filteredAssign.length}</span>
                )}
              </p>
              <p className="cm-review-hint">
                Content assigned to you by the admin for peer review.
              </p>

              <div className="cm-tabs">
                {(['all','guide','video','quiz'] as const).map(t => (
                  <button key={t} className={`cm-tab${reviewTab===t?' active':''}`} onClick={() => setReviewTab(t)}>
                    {t === 'all' ? 'All' : capitalise(t)+'s'}
                  </button>
                ))}
              </div>

              {!loading && (
                filteredAssign.length === 0
                  ? <div className="cm-empty"><p>No content assigned for review.</p></div>
                  : <div className="cm-list">
                      {filteredAssign.map(item => (
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
                            <p style={{ fontSize:13, color:'var(--text-muted)', lineHeight:1.5, marginBottom:12 }}>
                              {item.description}
                            </p>
                          )}

                          {/* Full content detail for review */}
                          {item.content_type === 'guide' && item.steps && item.steps.length > 0 && (
                            <div style={{ marginBottom: 14 }}>
                              <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                                Steps ({item.steps.length})
                              </p>
                              <ol style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                                {item.steps.map((step, idx) => (
                                  <li key={idx} style={{ fontSize: 13, lineHeight: 1.5 }}>{step}</li>
                                ))}
                              </ol>
                            </div>
                          )}

                          {item.content_type === 'video' && item.videoURL && (
                            <div style={{ marginBottom: 14 }}>
                              <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                                Video{item.durationSec ? ` · ${Math.floor(item.durationSec / 60)}m ${item.durationSec % 60}s` : ''}
                              </p>
                              <iframe
                                src={item.videoURL}
                                style={{ width: '100%', aspectRatio: '16/9', border: 'none', borderRadius: 8 }}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                              />
                            </div>
                          )}

                          {item.content_type === 'quiz' && item.questions && item.questions.length > 0 && (
                            <div style={{ marginBottom: 14 }}>
                              <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                                Questions ({item.questions.length})
                              </p>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                {item.questions.map((q, qi) => (
                                  <div key={q.questionID ?? qi} style={{ border: '1px solid var(--border)', borderRadius: 8, padding: 10 }}>
                                    <p style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{qi + 1}. {q.questionText}</p>
                                    <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4 }}>
                                      {q.answers.map((a, ai) => (
                                        <li key={a.answerID ?? ai} style={{ fontSize: 13, color: a.isCorrect ? 'var(--success, #16a34a)' : 'inherit', fontWeight: a.isCorrect ? 600 : 400 }}>
                                          {a.answerText}{a.isCorrect ? ' ✓' : ''}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="cm-form__group" style={{ marginBottom:12 }}>
                            <label>
                              Comment{' '}
                              <span style={{ fontWeight:400, color:'var(--text-muted)' }}>(required for rejection)</span>
                            </label>
                            <textarea rows={2} placeholder="Add feedback for the author…"
                              value={comments[item.contentID] ?? ''}
                              onChange={e => setComments(prev => ({ ...prev, [item.contentID]: e.target.value }))} />
                          </div>
                          <div className="cm-list-item__actions">
                            <button className="cm-action-btn cm-action-btn--success"
                              onClick={() => handleReview(item.contentID, 'verified')}>Verify</button>
                            <button className="cm-action-btn cm-action-btn--danger"
                              onClick={() => handleReview(item.contentID, 'rejected')}>Reject</button>
                          </div>
                        </div>
                      ))}
                    </div>
              )}

        </div>
      </div>
    </>
  )
}
