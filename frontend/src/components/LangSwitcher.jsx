import { LANGS } from '../i18n/translations.js'
import { useLang } from '../i18n/LangContext.jsx'

export default function LangSwitcher() {
  const { lang, setLang, t } = useLang()
  return (
    <div role="group" aria-label={t.nav.language} dir="ltr" className="flex rounded-full bg-grape-night/10 p-0.5">
      {LANGS.map((l) => (
        <button
          key={l.code}
          onClick={() => setLang(l.code)}
          aria-pressed={lang === l.code}
          aria-label={l.name}
          title={l.name}
          className={`rounded-full px-2.5 py-0.5 font-baloo text-xs font-bold transition ${lang === l.code ? 'bg-grape-night text-sun' : 'text-grape-night hover:bg-grape-night/10'}`}
        >
          {l.short}
        </button>
      ))}
    </div>
  )
}
