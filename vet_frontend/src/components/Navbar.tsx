import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container navbar__inner">

        {/* Logo */}
        <a href="/" className="navbar__logo">
          {/* <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
            <circle cx="14" cy="14" r="14" fill="#0d9488" opacity=".12"/>
            <ellipse cx="9"  cy="9"  rx="2.5" ry="3.2" fill="#0d9488"/>
            <ellipse cx="19" cy="9"  rx="2.5" ry="3.2" fill="#0d9488"/>
            <ellipse cx="5"  cy="14" rx="2.2" ry="3"   fill="#0d9488"/>
            <ellipse cx="23" cy="14" rx="2.2" ry="3"   fill="#0d9488"/>
            <path d="M14 12c-4.5 0-7 3-6 6.5C9 22 11.5 23.5 14 23.5s5-1.5 6-5c1-3.5-1.5-6.5-6-6.5z" fill="#0d9488"/>
          </svg> */}
          PawCare
        </a>

        {/* Nav links */}
        <ul className="navbar__links">
          <li><a href="/">Home</a></li>
          <li><a href="/guides">First Aid Guides</a></li>
          <li><a href="/videos">Videos</a></li>
          <li><a href="/quizzes">Quizzes</a></li>
          <li><a href="/book">Book a Vet</a></li>
        </ul>

        {/* Actions */}
        <div className="navbar__actions">
          <a href="/login" className="btn btn--ghost">Log in</a>
          <a href="/register" className="btn btn--primary">Get Started</a>
        </div>

      </div>
    </nav>
  )
}
