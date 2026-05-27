import { Link, NavLink } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
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
          <li><NavLink to="/book">Book a Vet</NavLink></li>
        </ul>

        <div className="navbar__actions">
          <Link to="/login" className="btn btn--ghost">Log in</Link>
          <Link to="/register" className="btn btn--primary">Get Started</Link>
        </div>

      </div>
    </nav>
  )
}
