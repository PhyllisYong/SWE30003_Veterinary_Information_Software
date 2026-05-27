import './HomePage.css'

const FEATURES = [
  {
    emoji: '📋',
    bg: '#e0f2fe',
    title: 'First Aid Guides',
    desc: 'Step-by-step emergency procedures written and verified by qualified veterinarians — available offline.',
    href: '/guides',
  },
  {
    emoji: '🎬',
    bg: '#fef9c3',
    title: 'Instructional Videos',
    desc: 'Watch concise how-to videos covering common emergencies for cats, dogs, and small pets.',
    href: '/videos',
  },
  {
    emoji: '🧠',
    bg: '#f3e8ff',
    title: 'Knowledge Quizzes',
    desc: 'Test your first-aid knowledge with vet-reviewed quizzes and track your progress over time.',
    href: '/quizzes',
  },
  {
    emoji: '💬',
    bg: '#dcfce7',
    title: 'Chat with a Vet',
    desc: 'Get advice from a licensed veterinarian - a quick chat or a consultation.',
    href: '/chat',
  }
]

const PETS = [
  { emoji: '🐱', label: 'Cats' },
  { emoji: '🐶', label: 'Dogs' },
  { emoji: '🐰', label: 'Rabbits' },
  { emoji: '🐹', label: 'Hamsters' },
  { emoji: '🐾', label: 'Guinea Pigs' },
]

const STEPS = [
  {
    n: '1',
    title: 'Create your free account',
    desc: 'Register as a pet owner and add your pets in under two minutes.',
  },
  {
    n: '2',
    title: 'Find the right content',
    desc: 'Search guides, videos, and quizzes filtered by pet type and emergency category.',
  },
  {
    n: '3',
    title: 'Get help when it counts',
    desc: 'Chat with a vet instantly or book a consultation — all from one place.',
  },
]

export default function HomePage() {
  return (
    <main>

      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section className="hero">
        <div className="container hero__inner">

          <div className="hero__content">
            {/* <div className="hero__badge">
              <span className="hero__badge-dot" />
              Vet-verified information
            </div> */}

            <h1>
              Fast, reliable first aid<br />
              for your <span>pet</span>
            </h1>

            <p className="hero__sub">
              PawCare gives small pet owners instant access to vet-verified
              first-aid guides, video tutorials, and live veterinary advice —
              so you're always prepared.
            </p>

            {/* <div className="hero__ctas">
              <a href="/register" className="btn btn--primary btn--lg">
                Get started free
              </a>
              <a href="/guides" className="btn btn--outline btn--lg">
                Browse guides
              </a>
            </div> */}

            <div className="hero__trust">
              <div className="hero__trust-avatars">
                {['🧑', '👩', '🧑‍⚕️', '👨'].map((e, i) => (
                  <div key={i} className="hero__trust-avatar">{e}</div>
                ))}
              </div>
              Trusted by 10,000+ pet owners
            </div>
          </div>

          {/* Emergency quick-access card */}
          <div className="hero__card">
            <div className="hero__card-header">
              <div className="hero__card-icon">🚨</div>
              <div>
                <h3>Emergency Categories</h3>
                <p>Tap a category to view guides</p>
              </div>
            </div>

            <div className="hero__card-list">
              {[
                ['🫁', 'Choking & Breathing'],
                ['🩹', 'Wounds & Bleeding'],
                ['☠️', 'Poisoning & Ingestion'],
                ['🦴', 'Fractures & Injuries'],
                ['🌡️', 'Heatstroke & Shock'],
              ].map(([emoji, label]) => (
                <a href="/guides" key={label} className="hero__card-item">
                  <span className="hero__card-item-emoji">{emoji}</span>
                  <span className="hero__card-item-text">{label}</span>
                  <span className="hero__card-item-arrow">›</span>
                </a>
              ))}
            </div>

            <a href="/guides" className="hero__card-link">
              View all guides →
            </a>
          </div>

        </div>
      </section>

      {/* ── Stats strip ──────────────────────────────────────────── */}
      <section className="stats">
        <div className="container">
          <div className="stats__grid">
            {[
              { n: '500+',   label: 'First-aid guides' },
              { n: '50+',    label: 'Licensed veterinarians' },
              { n: '10,000+', label: 'Pet owners helped' },
            ].map(({ n, label }) => (
              <div key={label} className="stats__item">
                <div className="stats__item-number">{n}</div>
                <div className="stats__item-label">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────── */}
      <section className="features">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">What we offer</span>
            <h2>Everything your pet needs, in one place</h2>
            <p>From emergency guides to live vet consultations — PawCare covers every aspect of your pet's wellbeing.</p>
          </div>

          <div className="features__grid">
            {FEATURES.map((f) => (
              <div key={f.title} className="feature-card">
                <div className="feature-card__icon" style={{ background: f.bg }}>
                  {f.emoji}
                </div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
                <a href={f.href} className="feature-card__link">
                  Learn more <span>→</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pets covered ─────────────────────────────────────────── */}
      <section className="pets">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Supported pets</span>
            <h2>We cover the pets you love</h2>
            <p>All content is categorised by pet type so you always find the right information fast.</p>
          </div>

          <div className="pets__grid">
            {PETS.map(({ emoji, label }) => (
              <a href={`/guides?pet=${label.toLowerCase()}`} key={label} className="pet-chip">
                <span>{emoji}</span>
                <span>{label}</span>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ─────────────────────────────────────────── */}
      {/* <section className="how">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">How it works</span>
            <h2>Up and running in minutes</h2>
          </div>

          <div className="how__steps">
            {STEPS.map((s) => (
              <div key={s.n} className="how-step">
                <div className="how-step__number">{s.n}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section> */}

      {/* ── CTA banner ───────────────────────────────────────────── */}
      <section className="cta-banner">
        <div className="container">
          <h2>Ready to protect your pet?</h2>
          <p>Join thousands of responsible pet owners. It's free to get started.</p>
          <a href="/register" className="btn btn--white btn--lg">
            Create a free account
          </a>
        </div>
      </section>

    </main>
  )
}
