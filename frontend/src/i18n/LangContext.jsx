import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { LANGS, translations } from './translations.js'

const LangContext = createContext(null)
const KEY = 'petmatch-lang'

function initialLang() {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved && translations[saved]) return saved
  } catch { /* stockage indisponible */ }
  return 'en' // anglais = langue officielle par défaut
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(initialLang)
  const meta = LANGS.find((l) => l.code === lang)

  useEffect(() => {
    document.documentElement.lang = lang
    document.documentElement.dir = meta.dir
    try { localStorage.setItem(KEY, lang) } catch { /* ignore */ }
  }, [lang, meta.dir])

  const value = useMemo(() => ({ lang, setLang, dir: meta.dir, t: translations[lang] }), [lang, meta.dir])
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>
}

export const useLang = () => useContext(LangContext)
