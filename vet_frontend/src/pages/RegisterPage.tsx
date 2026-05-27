import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './RegisterPage.css'

type Role = 'pet_owner' | 'veterinarian' | 'association_admin'

const ROLE_LABELS: Record<Role, string> = {
  pet_owner: 'Pet Owner',
  veterinarian: 'Veterinarian',
  association_admin: 'Association Administrator',
}

export default function RegisterPage() {
  const navigate = useNavigate()

  // Core fields
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [role, setRole] = useState<Role>('pet_owner')

  // Role-specific fields
  const [contactNumber, setContactNumber] = useState('')
  const [licenseNumber, setLicenseNumber] = useState('')
  const [specialisation, setSpecialisation] = useState('')
  const [workID, setWorkID] = useState('')

  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // ── client-side validation ──────────────────────────────────────────────────
  function validate(): string | null {
    if (!name.trim()) return 'Full name is required.'
    if (!email.trim()) return 'Email is required.'
    if (password.length < 8) return 'Password must be at least 8 characters.'
    if (password !== confirm) return 'Passwords do not match.'
    if (role === 'veterinarian' && !licenseNumber.trim())
      return 'License number is required for veterinarians.'
    if (role === 'association_admin' && !workID.trim())
      return 'Work ID is required for association administrators.'
    return null
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    const payload: Record<string, string> = { name, email, password, role }
    if (role === 'pet_owner' && contactNumber.trim())
      payload.contactNumber = contactNumber.trim()
    if (role === 'veterinarian') {
      payload.licenseNumber = licenseNumber.trim()
      if (specialisation.trim()) payload.specialisation = specialisation.trim()
    }
    if (role === 'association_admin') payload.workID = workID.trim()

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const body = await res.json()

      if (!res.ok) {
        setError(body.detail ?? 'Registration failed. Please try again.')
        return
      }

      // Same storage pattern as LoginPage
      localStorage.setItem('token', body.data.token)
      localStorage.setItem('userID', body.data.userID)
      localStorage.setItem('userName', body.data.name)
      localStorage.setItem('userRole', body.data.role)
      window.dispatchEvent(new Event('auth-change'))

      navigate('/', { replace: true })
    } catch {
      setError('Could not reach the server. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const canSubmit =
    !loading &&
    name.trim() &&
    email.trim() &&
    password &&
    confirm &&
    (role !== 'veterinarian' || licenseNumber.trim()) &&
    (role !== 'association_admin' || workID.trim())

  return (
    <div className="register-page">
      <div className="register-card">
        <h1>Create your account</h1>
        <p className="register-card__sub">
          Join PawCare to track your pets, take quizzes, and connect with vets.
        </p>

        {error && <div className="register-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          {/* ── Core fields ── */}
          <div className="rform-group">
            <label htmlFor="name">Full name</label>
            <input
              id="name"
              type="text"
              placeholder="Jane Smith"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="name"
            />
          </div>

          <div className="rform-group">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="rform-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="rform-group">
            <label htmlFor="confirm">Confirm password</label>
            <input
              id="confirm"
              type="password"
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          {/* ── Role selector ── */}
          <div className="rform-group">
            <label htmlFor="role">I am a…</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
            >
              {(Object.keys(ROLE_LABELS) as Role[]).map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABELS[r]}
                </option>
              ))}
            </select>
          </div>

          {/* ── Pet owner extras ── */}
          {role === 'pet_owner' && (
            <div className="rform-group">
              <label htmlFor="contactNumber">
                Contact number <span className="rform-optional">(optional)</span>
              </label>
              <input
                id="contactNumber"
                type="tel"
                placeholder="+61 4XX XXX XXX"
                value={contactNumber}
                onChange={(e) => setContactNumber(e.target.value)}
                autoComplete="tel"
              />
            </div>
          )}

          {/* ── Veterinarian extras ── */}
          {role === 'veterinarian' && (
            <>
              <div className="rform-group">
                <label htmlFor="licenseNumber">License number</label>
                <input
                  id="licenseNumber"
                  type="text"
                  placeholder="e.g. VIC-12345"
                  value={licenseNumber}
                  onChange={(e) => setLicenseNumber(e.target.value)}
                  required
                />
              </div>
              <div className="rform-group">
                <label htmlFor="specialisation">
                  Specialisation <span className="rform-optional">(optional)</span>
                </label>
                <input
                  id="specialisation"
                  type="text"
                  placeholder="e.g. Small Animal Surgery"
                  value={specialisation}
                  onChange={(e) => setSpecialisation(e.target.value)}
                />
              </div>
            </>
          )}

          {/* ── Association admin extras ── */}
          {role === 'association_admin' && (
            <div className="rform-group">
              <label htmlFor="workID">Work ID</label>
              <input
                id="workID"
                type="text"
                placeholder="e.g. AVA-98765"
                value={workID}
                onChange={(e) => setWorkID(e.target.value)}
                required
              />
            </div>
          )}

          <button
            type="submit"
            className="btn btn--primary register-submit"
            disabled={!canSubmit}
          >
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <div className="register-card__footer">
          Already have an account?{' '}
          <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  )
}
