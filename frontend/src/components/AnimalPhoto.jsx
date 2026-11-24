import { useState } from 'react'
import { EMOJI } from '../lib/data.js'

// Photo d'animal avec repli (emoji) si le fichier est introuvable.
export default function AnimalPhoto({ src, alt, espece, className = '' }) {
  const [failed, setFailed] = useState(false)
  if (!src || failed) {
    return (
      <div role="img" aria-label={alt} className={`flex items-center justify-center bg-grape-soft text-6xl ${className}`}>
        {EMOJI[espece] || '🐾'}
      </div>
    )
  }
  return <img src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} className={`object-cover object-[50%_30%] ${className}`} />
}
