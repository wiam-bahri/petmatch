export function Paw({ className = 'h-7 w-7' }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      <g fill="currentColor">
        <ellipse cx="14" cy="28" rx="7" ry="9" transform="rotate(-20 14 28)" />
        <ellipse cx="26" cy="15" rx="7" ry="10" transform="rotate(-8 26 15)" />
        <ellipse cx="40" cy="15" rx="7" ry="10" transform="rotate(8 40 15)" />
        <ellipse cx="52" cy="28" rx="7" ry="9" transform="rotate(20 52 28)" />
        <path d="M32 29c-9 0-18 9-18 18 0 6 5 9 10 8 4-1 5-2 8-2s4 1 8 2c5 1 10-2 10-8 0-9-9-18-18-18z" />
      </g>
    </svg>
  )
}

export function Check({ className = 'h-5 w-5' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="12" fill="#FFD83D" />
      <path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#4B34D1" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// Contours « nuages » décoratifs du hero
export function Doodle({ className = '' }) {
  return (
    <svg viewBox="0 0 300 420" className={className} aria-hidden="true" fill="none" stroke="rgba(255,255,255,.38)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M40 330c-30-10-34-52-8-66-18-26 4-60 36-52 4-34 52-44 70-14 28-18 66 6 56 40 34 6 40 52 8 64 16 28-10 58-44 46-14 26-58 24-70-4-26 10-52-2-48-14z" />
    </svg>
  )
}
