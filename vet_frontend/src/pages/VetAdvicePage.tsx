import { Link } from 'react-router-dom'
import './VetAdvicePage.css'

export default function VetAdvicePage() {
  return (
    <div className="vet-advice-page">
      <div className="vet-advice-hero">
        <h1>Veterinary Advice</h1>
        <p>Choose how you'd like to connect with a veterinarian.</p>
      </div>

      <div className="vet-advice-options">
        <Link to="/vet-advice/chat" className="vet-advice-card">
          <span className="vet-advice-card__icon">💬</span>
          <h2>Chat Consultation</h2>
          <p>
            Send messages to a vet and receive advice online. Ideal for
            non-urgent questions or follow-ups.
          </p>
          <span className="btn btn--primary">Start chatting</span>
        </Link>

        <Link to="/vet-advice/booking" className="vet-advice-card">
          <span className="vet-advice-card__icon">📅</span>
          <h2>Physical Consultation</h2>
          <p>
            Book an in-person appointment at a time and clinic that suits
            you and your pet.
          </p>
          <span className="btn btn--primary">Book now</span>
        </Link>
      </div>
    </div>
  )
}
