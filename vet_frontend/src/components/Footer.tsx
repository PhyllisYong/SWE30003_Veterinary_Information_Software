import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">

        <div className="footer__grid">
          <div className="footer__brand">
            <div className="footer__brand-logo">
              {/* <svg width="24" height="24" viewBox="0 0 28 28" fill="none" aria-hidden="true">
                <ellipse cx="9"  cy="9"  rx="2.5" ry="3.2" fill="#0d9488"/>
                <ellipse cx="19" cy="9"  rx="2.5" ry="3.2" fill="#0d9488"/>
                <ellipse cx="5"  cy="14" rx="2.2" ry="3"   fill="#0d9488"/>
                <ellipse cx="23" cy="14" rx="2.2" ry="3"   fill="#0d9488"/>
                <path d="M14 12c-4.5 0-7 3-6 6.5C9 22 11.5 23.5 14 23.5s5-1.5 6-5c1-3.5-1.5-6.5-6-6.5z" fill="#0d9488"/>
              </svg> */}
              PawCare
            </div>
            <p>
              Fast, reliable first-aid information for small pet owners.
              Verified by qualified veterinarians.
            </p>
          </div>

          <div className="footer__col">
            <h4>Resources</h4>
            <ul>
              <li><a href="/guides">First Aid Guides</a></li>
              <li><a href="/videos">Videos</a></li>
              <li><a href="/quizzes">Quizzes</a></li>
            </ul>
          </div>

          <div className="footer__col">
            <h4>Vet Services</h4>
            <ul>
              <li><a href="/vet-advice">Vet Advice</a></li>
              <li><a href="/vet-advice/chat">Chat with a Vet</a></li>
              <li><a href="/vet-advice/booking">Book Appointment</a></li>
            </ul>
          </div>

          {/* <div className="footer__col">
            <h4>Account</h4>
            <ul>
              <li><a href="/login">Log In</a></li>
              <li><a href="/register">Register</a></li>
            </ul>
          </div> */}
        </div>

        <div className="footer__bottom">
          <span>© {new Date().getFullYear()} PawCare. All rights reserved.</span>
          <span>
            <a href="/privacy">Privacy Policy</a>
            {' · '}
            <a href="/terms">Terms of Use</a>
          </span>
        </div>

      </div>
    </footer>
  )
}
