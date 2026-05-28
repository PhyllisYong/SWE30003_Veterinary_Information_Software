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

  // Re-read whenever LoginPage / RegisterPage fires 'auth-change',
  // or when another tab logs in/out (native 'storage' event)
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

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userID')
    localStorage.removeItem('userName')
    localStorage.removeItem('userRole')
    setUserRole(null)
    window.dispatchEvent(new Event('auth-change'))
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="container navbar__inner">

        <Link to="/" className="navbar__logo">
          PawCare
        </Link>

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
              </ul>
            </li>
          )}
        </ul>

        <div className="navbar__actions">
          {userName ? (
            <>
              <span className="navbar__user">Hi, {userName.split(' ')[0]}</span>
              <Link to="/profile" className="btn btn--ghost">Profile</Link>
              <button className="btn btn--ghost" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--ghost">Log in</Link>
              <Link to="/register" className="btn btn--primary">Get Started</Link>
            </>
          )}
        </div>

      </div>
    </nav>
  )
}
