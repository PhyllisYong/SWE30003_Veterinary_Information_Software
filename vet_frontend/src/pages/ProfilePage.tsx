import { useState, useEffect, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import './ProfilePage.css'

// ── Types ──────────────────────────────────────────────────────────────────────
interface ProfileData {
  userID: string
  name: string
  email: string
  role: string
  contactNumber?: string | null   // pet_owner
  licenseNumber?: string | null   // veterinarian
  specialisation?: string | null  // veterinarian
  workID?: string | null          // association_admin
}

interface Pet {
  petID: string
  petName: string
  petType: string
  age: number | null
  gender: string | null
}

const PET_TYPES = ['cat', 'dog', 'rabbit', 'hamster', 'guinea_pig']
const GENDERS = ['male', 'female']

function capitalise(s: string): string {
  return s.replace(/_/g, ' ').charAt(0).toUpperCase() + s.replace(/_/g, ' ').slice(1)
}

// ── Component ──────────────────────────────────────────────────────────────────
export default function ProfilePage() {
  const navigate = useNavigate()
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole')
  const isPetOwner = userRole === 'pet_owner'
  const isVet      = userRole === 'veterinarian'
  const isAdmin    = userRole === 'association_admin'

  // ── Profile state ──
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [contactNumber, setContactNumber] = useState('')    // pet_owner
  const [licenseNumber, setLicenseNumber] = useState('')    // veterinarian (read-only)
  const [specialisation, setSpecialisation] = useState('') // veterinarian (editable)
  const [workID, setWorkID] = useState('')                  // association_admin (read-only)
  const [profileLoading, setProfileLoading] = useState(true)
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileError, setProfileError] = useState<string | null>(null)
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null)

  // ── Pets state ──
  const [pets, setPets] = useState<Pet[]>([])
  const [petsError, setPetsError] = useState<string | null>(null)

  // ── Add pet form ──
  const [showAddForm, setShowAddForm] = useState(false)
  const [addPetName, setAddPetName] = useState('')
  const [addPetType, setAddPetType] = useState('cat')
  const [addPetAge, setAddPetAge] = useState('')
  const [addPetGender, setAddPetGender] = useState('')
  const [addPetSaving, setAddPetSaving] = useState(false)
  const [addPetError, setAddPetError] = useState<string | null>(null)

  // ── Edit pet inline ──
  const [editingPetID, setEditingPetID] = useState<string | null>(null)
  const [editPetName, setEditPetName] = useState('')
  const [editPetType, setEditPetType] = useState('')
  const [editPetAge, setEditPetAge] = useState('')
  const [editPetGender, setEditPetGender] = useState('')
  const [editPetSaving, setEditPetSaving] = useState(false)
  const [editPetError, setEditPetError] = useState<string | null>(null)

  // ── Auth guard ──
  useEffect(() => {
    if (!token) {
      navigate('/login?redirect=/profile', { replace: true })
    }
  }, [token, navigate])

  // ── Fetch profile on mount ──
  useEffect(() => {
    if (!token) return

    fetch('/api/profile', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.status === 401) {
          navigate('/login?redirect=/profile', { replace: true })
          return Promise.reject('unauthorized')
        }
        if (!res.ok) throw new Error(`Server error: ${res.status}`)
        return res.json()
      })
      .then((body: { status: string; data: ProfileData }) => {
        const d = body.data
        setName(d.name)
        setEmail(d.email)
        // role-specific fields
        setContactNumber(d.contactNumber ?? '')
        setLicenseNumber(d.licenseNumber ?? '')
        setSpecialisation(d.specialisation ?? '')
        setWorkID(d.workID ?? '')
        setProfileLoading(false)
      })
      .catch((err) => {
        if (err !== 'unauthorized') {
          setProfileError('Could not load profile.')
          setProfileLoading(false)
        }
      })
  }, [token, navigate])

  // ── Fetch pets (pet_owner only) ──
  useEffect(() => {
    if (!token || !isPetOwner) return

    fetch('/api/pets', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`)
        return res.json()
      })
      .then((body: { status: string; data: Pet[] }) => {
        setPets(body.data)
      })
      .catch(() => {
        setPetsError('Could not load pets.')
      })
  }, [token, isPetOwner])

  // ── Save profile ──
  async function handleProfileSave(e: FormEvent) {
    e.preventDefault()
    setProfileError(null)
    setProfileSuccess(null)
    setProfileSaving(true)

    const payload: Record<string, string> = { name, email }
    if (isPetOwner && contactNumber.trim()) payload.contactNumber = contactNumber.trim()
    if (isVet) payload.specialisation = specialisation

    try {
      const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
      const body = await res.json()
      if (!res.ok) {
        setProfileError(body.detail ?? 'Failed to save profile.')
        return
      }
      // Update Navbar greeting
      localStorage.setItem('userName', name)
      window.dispatchEvent(new Event('auth-change'))
      setProfileSuccess('Profile updated successfully.')
    } catch {
      setProfileError('Could not reach the server.')
    } finally {
      setProfileSaving(false)
    }
  }

  // ── Add pet ──
  async function handleAddPet(e: FormEvent) {
    e.preventDefault()
    setAddPetError(null)
    setAddPetSaving(true)

    const payload: Record<string, string | number> = {
      petName: addPetName,
      petType: addPetType,
    }
    if (addPetAge.trim()) payload.age = parseInt(addPetAge, 10)
    if (addPetGender) payload.gender = addPetGender

    try {
      const res = await fetch('/api/pets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
      const body = await res.json()
      if (!res.ok) {
        setAddPetError(body.detail ?? 'Failed to add pet.')
        return
      }
      setPets((prev) => [body.data, ...prev])
      setShowAddForm(false)
      setAddPetName('')
      setAddPetType('cat')
      setAddPetAge('')
      setAddPetGender('')
    } catch {
      setAddPetError('Could not reach the server.')
    } finally {
      setAddPetSaving(false)
    }
  }

  // ── Start editing a pet ──
  function startEditPet(pet: Pet) {
    setEditingPetID(pet.petID)
    setEditPetName(pet.petName)
    setEditPetType(pet.petType)
    setEditPetAge(pet.age != null ? String(pet.age) : '')
    setEditPetGender(pet.gender ?? '')
    setEditPetError(null)
  }

  // ── Save edited pet ──
  async function handleEditPet(e: FormEvent, petID: string) {
    e.preventDefault()
    setEditPetError(null)
    setEditPetSaving(true)

    const payload: Record<string, string | number> = {
      petName: editPetName,
      petType: editPetType,
    }
    if (editPetAge.trim()) payload.age = parseInt(editPetAge, 10)
    if (editPetGender) payload.gender = editPetGender

    try {
      const res = await fetch(`/api/pets/${petID}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
      const body = await res.json()
      if (!res.ok) {
        setEditPetError(body.detail ?? 'Failed to update pet.')
        return
      }
      setPets((prev) =>
        prev.map((p) => (p.petID === petID ? body.data : p))
      )
      setEditingPetID(null)
    } catch {
      setEditPetError('Could not reach the server.')
    } finally {
      setEditPetSaving(false)
    }
  }

  // ── Delete pet ──
  async function handleDeletePet(petID: string, petName: string) {
    if (!window.confirm(`Remove ${petName} from your pets?`)) return

    try {
      const res = await fetch(`/api/pets/${petID}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return
      setPets((prev) => prev.filter((p) => p.petID !== petID))
    } catch {
      // silently ignore
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Page header */}
      <div className="profile-header">
        <div className="container">
          <h1>My Profile</h1>
          <p>
            Manage your account details
            {isPetOwner ? ' and your pets' : isVet ? ' and your specialisation' : ''}.
          </p>
        </div>
      </div>

      {/* Body */}
      <div className="profile-body">
        <div className="container">

          {profileLoading ? (
            <div className="profile-empty"><p>Loading profile…</p></div>
          ) : (

            <>
              {/* ── Profile card ── */}
              <div className="profile-card">
                <h2 className="profile-card__title">Account Information</h2>

                {profileError && (
                  <div className="profile-banner profile-banner--error">{profileError}</div>
                )}
                {profileSuccess && (
                  <div className="profile-banner profile-banner--success">{profileSuccess}</div>
                )}

                <form onSubmit={handleProfileSave} noValidate>
                  <div className="pform-group">
                    <label htmlFor="prof-name">Full name</label>
                    <input
                      id="prof-name"
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      autoComplete="name"
                    />
                  </div>

                  <div className="pform-group">
                    <label htmlFor="prof-email">Email address</label>
                    <input
                      id="prof-email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      autoComplete="email"
                    />
                  </div>

                  {/* ── pet_owner extras ── */}
                  {isPetOwner && (
                    <div className="pform-group">
                      <label htmlFor="prof-contact">
                        Contact number{' '}
                        <span className="pform-optional">(optional)</span>
                      </label>
                      <input
                        id="prof-contact"
                        type="tel"
                        value={contactNumber}
                        onChange={(e) => setContactNumber(e.target.value)}
                        autoComplete="tel"
                        placeholder="+60 1X-XXXXXXX"
                      />
                    </div>
                  )}

                  {/* ── veterinarian extras ── */}
                  {isVet && (
                    <>
                      <div className="pform-group">
                        <label>License Number</label>
                        <input
                          type="text"
                          value={licenseNumber}
                          readOnly
                          className="pform-readonly"
                        />
                      </div>
                      <div className="pform-group">
                        <label htmlFor="prof-specialisation">
                          Specialisation{' '}
                          <span className="pform-optional">(optional)</span>
                        </label>
                        <input
                          id="prof-specialisation"
                          type="text"
                          value={specialisation}
                          onChange={(e) => setSpecialisation(e.target.value)}
                          placeholder="e.g. Small Animal Surgery"
                        />
                      </div>
                    </>
                  )}

                  {/* ── association_admin extras ── */}
                  {isAdmin && (
                    <div className="pform-group">
                      <label>Work ID</label>
                      <input
                        type="text"
                        value={workID}
                        readOnly
                        className="pform-readonly"
                      />
                    </div>
                  )}

                  <button
                    type="submit"
                    className="btn btn--primary profile-save-btn"
                    disabled={profileSaving || !name.trim() || !email.trim()}
                  >
                    {profileSaving ? 'Saving…' : 'Save Changes'}
                  </button>
                </form>
              </div>

              {/* ── Pets card (pet_owner only) ── */}
              {isPetOwner && (
                <div className="profile-card">
                  <div className="pets-section-header">
                    <h2 className="profile-card__title">My Pets</h2>
                    {!showAddForm && (
                      <button
                        className="btn btn--outline"
                        onClick={() => {
                          setShowAddForm(true)
                          setAddPetError(null)
                        }}
                      >
                        + Add Pet
                      </button>
                    )}
                  </div>

                  {petsError && (
                    <div className="profile-banner profile-banner--error">{petsError}</div>
                  )}

                  {/* Add pet form */}
                  {showAddForm && (
                    <form
                      className="pet-inline-form"
                      onSubmit={handleAddPet}
                      noValidate
                    >
                      <h3 className="pet-inline-form__title">New Pet</h3>
                      {addPetError && (
                        <div className="profile-banner profile-banner--error">{addPetError}</div>
                      )}
                      <div className="pform-row">
                        <div className="pform-group">
                          <label htmlFor="add-pet-name">Pet name</label>
                          <input
                            id="add-pet-name"
                            type="text"
                            value={addPetName}
                            onChange={(e) => setAddPetName(e.target.value)}
                            required
                            placeholder="e.g. Whiskers"
                          />
                        </div>
                        <div className="pform-group">
                          <label htmlFor="add-pet-type">Type</label>
                          <select
                            id="add-pet-type"
                            value={addPetType}
                            onChange={(e) => setAddPetType(e.target.value)}
                          >
                            {PET_TYPES.map((t) => (
                              <option key={t} value={t}>{capitalise(t)}</option>
                            ))}
                          </select>
                        </div>
                        <div className="pform-group">
                          <label htmlFor="add-pet-age">
                            Age <span className="pform-optional">(yrs)</span>
                          </label>
                          <input
                            id="add-pet-age"
                            type="number"
                            min="0"
                            max="40"
                            value={addPetAge}
                            onChange={(e) => setAddPetAge(e.target.value)}
                            placeholder="—"
                          />
                        </div>
                        <div className="pform-group">
                          <label htmlFor="add-pet-gender">Gender</label>
                          <select
                            id="add-pet-gender"
                            value={addPetGender}
                            onChange={(e) => setAddPetGender(e.target.value)}
                          >
                            <option value="">—</option>
                            {GENDERS.map((g) => (
                              <option key={g} value={g}>{capitalise(g)}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="pet-inline-form__actions">
                        <button
                          type="submit"
                          className="btn btn--primary"
                          disabled={addPetSaving || !addPetName.trim()}
                        >
                          {addPetSaving ? 'Adding…' : 'Add Pet'}
                        </button>
                        <button
                          type="button"
                          className="btn btn--ghost"
                          onClick={() => {
                            setShowAddForm(false)
                            setAddPetName('')
                            setAddPetAge('')
                            setAddPetGender('')
                            setAddPetError(null)
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Edit pet form (above grid, full-width) */}
                  {editingPetID && (
                    <form
                      className="pet-inline-form"
                      onSubmit={(e) => handleEditPet(e, editingPetID)}
                      noValidate
                    >
                      <h3 className="pet-inline-form__title">Edit Pet</h3>
                      {editPetError && (
                        <div className="profile-banner profile-banner--error">{editPetError}</div>
                      )}
                      <div className="pform-row">
                        <div className="pform-group">
                          <label>Pet name</label>
                          <input
                            type="text"
                            value={editPetName}
                            onChange={(e) => setEditPetName(e.target.value)}
                            required
                          />
                        </div>
                        <div className="pform-group">
                          <label>Type</label>
                          <select
                            value={editPetType}
                            onChange={(e) => setEditPetType(e.target.value)}
                          >
                            {PET_TYPES.map((t) => (
                              <option key={t} value={t}>{capitalise(t)}</option>
                            ))}
                          </select>
                        </div>
                        <div className="pform-group">
                          <label>Age <span className="pform-optional">(yrs)</span></label>
                          <input
                            type="number"
                            min="0"
                            max="40"
                            value={editPetAge}
                            onChange={(e) => setEditPetAge(e.target.value)}
                            placeholder="—"
                          />
                        </div>
                        <div className="pform-group">
                          <label>Gender</label>
                          <select
                            value={editPetGender}
                            onChange={(e) => setEditPetGender(e.target.value)}
                          >
                            <option value="">—</option>
                            {GENDERS.map((g) => (
                              <option key={g} value={g}>{capitalise(g)}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="pet-inline-form__actions">
                        <button
                          type="submit"
                          className="btn btn--primary"
                          disabled={editPetSaving || !editPetName.trim()}
                        >
                          {editPetSaving ? 'Saving…' : 'Save'}
                        </button>
                        <button
                          type="button"
                          className="btn btn--ghost"
                          onClick={() => setEditingPetID(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Pets grid */}
                  {pets.length === 0 && !showAddForm ? (
                    <div className="profile-empty">
                      <p>You haven't added any pets yet. Click <strong>+ Add Pet</strong> to get started.</p>
                    </div>
                  ) : (
                    <div className="pet-grid">
                      {pets.map((pet) => (
                        <div
                          key={pet.petID}
                          className={`pet-card${editingPetID === pet.petID ? ' pet-card--editing' : ''}`}
                        >
                          <div className="pet-card__icon">
                            {pet.petType === 'dog' ? '🐕' :
                             pet.petType === 'cat' ? '🐈' :
                             pet.petType === 'rabbit' ? '🐇' :
                             pet.petType === 'hamster' ? '🐹' : '🐾'}
                          </div>
                          <h3 className="pet-card__name">{pet.petName}</h3>
                          <p className="pet-card__detail">{capitalise(pet.petType)}</p>
                          {(pet.age != null || pet.gender) && (
                            <p className="pet-card__detail pet-card__detail--muted">
                              {[
                                pet.age != null ? `${pet.age} yr${pet.age !== 1 ? 's' : ''}` : null,
                                pet.gender ? capitalise(pet.gender) : null,
                              ]
                                .filter(Boolean)
                                .join(' · ')}
                            </p>
                          )}
                          <div className="pet-card__actions">
                            <button
                              className="btn btn--outline btn--sm"
                              onClick={() => startEditPet(pet)}
                              disabled={!!editingPetID && editingPetID !== pet.petID}
                            >
                              Edit
                            </button>
                            <button
                              className="btn btn--ghost btn--sm pet-card__delete"
                              onClick={() => handleDeletePet(pet.petID, pet.petName)}
                              disabled={!!editingPetID}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

        </div>
      </div>
    </>
  )
}
