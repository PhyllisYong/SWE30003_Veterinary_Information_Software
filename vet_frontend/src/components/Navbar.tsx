import { useState, useEffect } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import './Navbar.css'

function readUser() {
  return localStorage.getItem('userName')
}

function readRole() {
  return localStorage.getItem('userRole')
}

export default function Navbar() {
  const navigate = useNavigate()
  const [userName, setUserName] = useState<string | null>(readUser)
  const [userRole, setUserRole] = useState<string | null>(readRole)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    function sync() {
      setUserName(readUser())
      setUserRole(readRole())
    }
    window.addEventListener('auth-change', sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener('auth-change', sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  // Close mobile menu on route change
  useEffect(() => { setMenuOpen(false) }, [])

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userID')
    localStorage.removeItem('userName')
    localStorage.removeItem('userRole')
    setUserRole(null)
    window.dispatchEvent(new Event('auth-change'))
    setMenuOpen(false)
    navigate('/')
  }

  const firstName = userName ? userName.split(' ')[0] : ''

  return (
    <nav className="navbar">
      <div className="container navbar__inner">

        <Link to="/" className="navbar__logo">
          PawCare
        </Link>

        {/* Desktop nav links */}
        <ul className="navbar__links">
          <li><NavLink to="/" end>Home</NavLink></li>
          <li><NavLink to="/guides">First Aid Guides</NavLink></li>
          <li><NavLink to="/videos">Videos</NavLink></li>
          <li><NavLink to="/quizzes">Quizzes</NavLink></li>
          <li><NavLink to="/vet-advice">Vet Advice</NavLink></li>
          {userRole === 'veterinarian' && (
            <li className="navbar__dropdown">
              <span className="navbar__dropdown-trigger">Vet Tools ▾</span>
              <ul className="navbar__dropdown-menu">
                <li><NavLink to="/vet/availability">My Availability</NavLink></li>
                <li><NavLink to="/vet/quiz-manage">Quiz Explanations</NavLink></li>
                <li><NavLink to="/vet/video-manage">Video Manager</NavLink></li>
                <li><NavLink to="/vet/content-management">Content Management</NavLink></li>
              </ul>
            </li>
           
          )}
          {
            (userRole === 'association_admin' )&& (
             <li><NavLink to="/admin/content-management">Content Management</NavLink></li>)          }
        </ul>

        {/* Desktop auth */}
        <div className="navbar__actions">
          {userName ? (
            <>
              
              <Link to="/profile" className="btn btn--ghost">{firstName}</Link>
              <button className="navbar__chip navbar__chip--logout" onClick={handleLogout}>
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--ghost">Log in</Link>
              <Link to="/register" className="btn btn--primary">Get Started</Link>
            </>
          )}
        </div>

        {/* Hamburger — mobile only */}
        <button
          className={`navbar__hamburger${menuOpen ? ' open' : ''}`}
          onClick={() => setMenuOpen(o => !o)}
          aria-label="Toggle menu"
        >
          <span /><span /><span />
        </button>

      </div>

      {/* Mobile drawer */}
      {menuOpen && (
        <div className="navbar__drawer">
          <ul className="navbar__drawer-links">
            <li><NavLink to="/" end onClick={() => setMenuOpen(false)}>Home</NavLink></li>
            <li><NavLink to="/guides" onClick={() => setMenuOpen(false)}>First Aid Guides</NavLink></li>
            <li><NavLink to="/videos" onClick={() => setMenuOpen(false)}>Videos</NavLink></li>
            <li><NavLink to="/quizzes" onClick={() => setMenuOpen(false)}>Quizzes</NavLink></li>
            <li><NavLink to="/book" onClick={() => setMenuOpen(false)}>Book a Vet</NavLink></li>
          </ul>

          <div className="navbar__drawer-auth">
            {userName ? (
              <>
                <span className="navbar__chip navbar__chip--user">{firstName}</span>
                <button className="navbar__chip navbar__chip--logout" onClick={handleLogout}>
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn--ghost" onClick={() => setMenuOpen(false)}>
                  Log in
                </Link>
                <Link to="/register" className="btn btn--primary" onClick={() => setMenuOpen(false)}>
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
