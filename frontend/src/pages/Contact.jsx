import { useLang } from '../i18n/LangContext.jsx'

const INSTAGRAM_URL = 'https://www.instagram.com/wiam.dev/'

/* Icônes SVG simples (style trait), même principe que components/Icons.jsx : aucune dépendance ajoutée. */
function Svg({ children, className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  )
}
const ICONS = {
  adoption: <Svg><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></Svg>,
  problem: <Svg><path d="M5 21V4" /><path d="M5 4h12l-2 4 2 4H5" /></Svg>,
  support: <Svg><path d="M14.7 6.3a4 4 0 0 0-5 5L4 17l3 3 5.7-5.7a4 4 0 0 0 5-5l-2.4 2.4-2.6-.6-.6-2.6z" /></Svg>,
  feedback: <Svg><path d="M9 18h6" /><path d="M10 21h4" /><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z" /></Svg>,
  other: <Svg><circle cx="12" cy="12" r="9" /><path d="M9.5 9.5a2.6 2.6 0 1 1 3.6 2.4c-.7.4-1.1 1-1.1 1.6" /><path d="M12 17h.01" /></Svg>,
}
const BADGE = { adoption: 'bg-bubble', problem: 'bg-tang', support: 'bg-sky', feedback: 'bg-sun', other: 'bg-mint' }

function Instagram({ className = 'h-8 w-8' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.2" cy="6.8" r="0.8" fill="currentColor" />
    </svg>
  )
}

export default function Contact() {
  const { t } = useLang()
  const c = t.contact
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="title text-5xl">{c.title[0]}<span className="text-sun">{c.title[1]}</span></h1>
      <p className="mt-3 font-baloo text-xl font-semibold text-white">{c.subtitle}</p>
      <p className="desc mt-3 max-w-2xl text-white/85">{c.desc}</p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <h2 className="font-baloo text-2xl font-bold text-sun">{c.catsTitle}</h2>
          <ul className="mt-4 grid gap-4 sm:grid-cols-2">
            {c.cats.map(([key, name, text], i) => (
              <li
                key={key}
                className={`flex items-start gap-3 rounded-[28px] bg-grape-soft p-4 transition hover:-translate-y-0.5 hover:bg-grape-soft/90 ${i === c.cats.length - 1 ? 'sm:col-span-2' : ''}`}
              >
                <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-grape-night ${BADGE[key]}`}>{ICONS[key]}</span>
                <div>
                  <h3 className="font-baloo text-lg font-bold leading-tight">{name}</h3>
                  <p className="desc mt-1 text-white/90">{text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <article className="h-fit rounded-[36px] bg-sun p-7 text-grape-night shadow-lg transition hover:-translate-y-1 hover:shadow-xl">
          <span className="flex h-16 w-16 items-center justify-center rounded-full bg-grape-night text-sun">
            <Instagram className="h-9 w-9" />
          </span>
          <h2 className="title mt-4 text-3xl">{c.devTitle}</h2>
          <p className="mt-1 font-baloo text-xl font-bold text-tang">@wiam.dev</p>
          <p className="desc mt-3 text-grape-night/85">{c.devText}</p>
          <a
            href={INSTAGRAM_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${c.btn} (${c.newTab})`}
            className="btn mt-6 w-full gap-2 hover:-translate-y-0.5"
          >
            <Instagram className="h-5 w-5" />
            {c.btn}
          </a>
        </article>
      </div>
    </section>
  )
}
