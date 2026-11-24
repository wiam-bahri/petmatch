import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getComments } from '../lib/api.js'
import { Check, Doodle } from '../components/Icons.jsx'
import { useLang } from '../i18n/LangContext.jsx'

/* Pastille ronde insérée dans un mot du titre (remplace un « o ») */
function Bubble({ children, className = '', ring = 'ring-mint' }) {
  return (
    <span className={`relative mx-[0.04em] inline-block h-[0.82em] w-[0.82em] -translate-y-[0.02em] overflow-hidden rounded-full align-middle ring-4 ${ring} ${className}`}>
      {children}
    </span>
  )
}

function Hero() {
  const { t } = useLang()
  const h = t.hero
  return (
    <section className="relative overflow-hidden">
      <Doodle className="pointer-events-none absolute -left-24 top-24 hidden h-[420px] w-[300px] md:block" />
      <Doodle className="pointer-events-none absolute -right-24 top-10 hidden h-[420px] w-[300px] scale-x-[-1] md:block" />

      <div className="relative mx-auto max-w-4xl px-5 pb-10 pt-14 text-center">
        <h1 className="title text-[44px] sm:text-6xl md:text-[80px]">
          <span className="block text-white">
            {h.l1[0]}
            {!h.plain && (
              <Bubble>
                <img src="/pets/puppy-kitten.webp" alt="" className="h-full w-full scale-150 object-cover object-center" />
              </Bubble>
            )}
            {h.l1[1]}
          </span>
          <span className="block text-white">
            {h.l2[0]}
            {!h.plain && (
              <Bubble className="bg-bubble text-grape-night" ring="ring-bubble/40">
                <span className="flex h-full w-full flex-col items-center justify-center font-baloo text-[0.2em] font-extrabold leading-none">
                  Top<br />5
                </span>
              </Bubble>
            )}
            {h.l2[1]}<span className="text-sun">{h.accent}</span>
          </span>
        </h1>

        <p className="desc mx-auto mt-6 max-w-md text-white/90">{h.desc}</p>
        <Link to="/matching" className="btn mt-5">{h.cta}</Link>

        <div className="relative mx-auto mt-24 max-w-3xl rounded-full border-[6px] border-sun bg-sun p-2">
          <div className="relative h-36 rounded-full border-[3px] border-white/60 bg-grape-deep sm:h-44">
            <img src="/pets/dog-friends.webp" alt={h.pillAlt} className="absolute bottom-0 left-1/2 h-[150%] max-w-none -translate-x-1/2 object-contain" />
          </div>
        </div>
      </div>
    </section>
  )
}

function About() {
  const { t } = useLang()
  const ab = t.about
  const points = ab.points
  return (
    <section className="mx-auto max-w-6xl px-4">
      <div className="grid items-center gap-8 rounded-[44px] bg-grape-soft p-8 md:grid-cols-2 md:p-12">
        <div className="relative mx-auto h-[330px] w-[290px] sm:h-[380px] sm:w-[340px]">
          <div className="absolute inset-0 overflow-hidden rounded-[32px] bg-sun">
            <img src="/pets/dog-paw.webp" alt={ab.dogAlt} className="absolute bottom-0 left-1/2 h-[96%] max-w-none -translate-x-[58%] object-contain" />
          </div>
          <div className="absolute -bottom-6 -right-6 h-40 w-40 rotate-6 overflow-hidden rounded-[26px] border-[5px] border-grape-soft bg-bubble sm:h-44 sm:w-44">
            <img src="/pets/puppy-kitten.webp" alt={ab.pupAlt} className="absolute bottom-1 left-1/2 w-[130%] max-w-none -translate-x-1/2 object-contain" />
          </div>
          <svg viewBox="0 0 60 50" className="absolute -right-2 top-0 h-12 w-14 text-sun" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round">
            <path d="M8 40l8-22M24 44l8-26M40 40l8-22" />
          </svg>
        </div>

        <div>
          <h2 className="title text-4xl md:text-5xl">
            {ab.title[0]}<span className="text-sun">{ab.title[1]}</span>
          </h2>
          <p className="desc mt-4 text-white/95">
            {ab.p}
          </p>
          <ul className="mt-5 space-y-3">
            {points.map((p) => (
              <li key={p} className="flex items-start gap-3">
                <Check className="mt-0.5 h-5 w-5 shrink-0" />
                <span className="desc font-normal text-white">{p}</span>
              </li>
            ))}
          </ul>
          <Link to="/animaux" className="btn mt-7">{ab.btn}</Link>
        </div>
      </div>
    </section>
  )
}

function Categories() {
  const { t } = useLang()
  const cats = [
    { label: t.cats.puppies, bg: 'bg-mint', img: '/pets/puppy-kitten.webp', to: '/animaux?espece=chien' },
    { label: t.cats.dogs, bg: 'bg-[#FFA24A]', img: '/pets/dog-paw.webp', to: '/animaux?espece=chien' },
    { label: t.cats.small, bg: 'bg-sun', img: '/pets/dog-friends.webp', to: '/animaux?espece=lapin' },
    { label: t.cats.all, bg: 'bg-bubble', img: '/pets/pet-group.webp', to: '/animaux' },
  ]
  return (
    <section className="mx-auto mt-16 max-w-6xl px-4">
      <div className="rounded-[44px] bg-sky/90 p-5 md:p-7">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {cats.map((c) => (
            <article key={c.label} className={`relative flex h-64 flex-col justify-end overflow-hidden rounded-[30px] ${c.bg}`}>
              <img src={c.img} alt="" className="absolute left-1/2 top-3 h-44 w-[88%] max-w-none -translate-x-1/2 object-contain" />
              <div className="m-3 flex items-center justify-between rounded-full bg-white/95 py-1.5 ps-4 pe-1.5 text-grape-night">
                <span className="font-baloo text-sm font-bold">{c.label}</span>
                <Link to={c.to} className="btn btn-sm !py-0.5">{t.cats.view}</Link>
              </div>
            </article>
          ))}
        </div>
        <div className="mt-6 flex justify-center">
          <Link to="/animaux" className="btn">{t.cats.more}</Link>
        </div>
      </div>
    </section>
  )
}

function Voices() {
  const { t } = useLang()
  const vo = t.voices
  const [latest, setLatest] = useState(null) // dernier VRAI commentaire général (aucun texte inventé)
  useEffect(() => { getComments({ limit: 1 }).then((d) => setLatest(d[0] || null)).catch(() => setLatest(null)) }, [])
  return (
    <section className="mx-auto mt-16 max-w-6xl px-4">
      <div className="grid items-center gap-8 md:grid-cols-[320px_1fr]">
        <div className="relative mx-auto h-[330px] w-[260px] overflow-hidden rounded-[32px] bg-sun">
          <img src="/pets/cat-hand.webp" alt={vo.alt} className="absolute left-1/2 top-4 w-[118%] max-w-none -translate-x-[54%] object-contain" />
          <div className="absolute bottom-4 left-3 right-3 rounded-2xl bg-mint p-3 shadow-lg">
            {latest ? (
              <>
                <p className="font-baloo text-sm font-bold text-grape-night">{latest.auteur}</p>
                <p className="desc line-clamp-4 break-words text-[11px] leading-snug text-grape-night/90">{latest.message}</p>
              </>
            ) : (
              <p className="desc text-[11px] leading-snug text-grape-night/90">{vo.empty}</p>
            )}
          </div>
        </div>
        <div>
          <h2 className="title text-4xl md:text-5xl">
            {vo.title[0]}<span className="text-tang">{vo.title[1]}</span>
          </h2>
          <p className="desc mt-4 max-w-md text-white/90">
            {vo.p}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/matching" className="btn">{vo.btn}</Link>
            <Link to="/avis" className="btn bg-white/15 text-white hover:bg-white/25">{vo.all}</Link>
          </div>
        </div>
      </div>

      <div className="mt-10 grid grid-cols-3 gap-4 rounded-[28px] bg-grape-night px-4 py-6 text-center md:px-10">
        {vo.stats.map(([n, l]) => (
          <div key={l}>
            <p className="title text-2xl text-sun md:text-4xl">{n}</p>
            <p className="desc mt-1 text-[11px] text-white/80">{l}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function Parcours() {
  const { t } = useLang()
  const jo = t.journey
  const style = [
    { bg: 'bg-[#FFA24A]', to: '/animaux' },
    { bg: 'bg-mint', to: '/matching' },
    { bg: 'bg-bubble', to: '/contact' },
  ]
  const cards = jo.cards.map((c, i) => ({ ...c, ...style[i] }))
  return (
    <section className="mx-auto mt-16 max-w-6xl px-4">
      <div className="rounded-[44px] bg-grape-soft p-6 md:p-10">
        <div className="flex items-end justify-between">
          <h2 className="title text-4xl md:text-5xl">
            {jo.title[0]}<span className="text-sun">{jo.title[1]}</span>
          </h2>
          <Link to="/animaux" className="desc text-white/90 underline underline-offset-4 hover:text-sun">{jo.more}</Link>
        </div>
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {cards.map((c) => (
            <article key={c.step} className={`rounded-[26px] p-5 text-grape-night ${c.bg}`}>
              <p className="desc font-medium">{c.step}</p>
              <p className="title mt-1 text-4xl">{c.big}</p>
              <p className="desc text-[11px]">{jo.free}</p>
              <Link to={c.to} className="btn btn-sm mt-4 w-full">{c.btn}</Link>
              <ul className="mt-4 space-y-2">
                {c.items.map((i) => (
                  <li key={i} className="flex items-center gap-2">
                    <Check className="h-4 w-4 shrink-0" />
                    <span className="desc text-[12px] font-normal">{i}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function Banner() {
  const { t } = useLang()
  const bn = t.banner
  return (
    <section className="mx-auto mb-16 mt-16 max-w-6xl px-4">
      <div className="relative flex min-h-[220px] flex-col justify-center overflow-hidden rounded-[36px] bg-sun p-8 text-grape-night md:flex-row md:items-center md:justify-between md:px-12">
        <div className="relative z-10 max-w-sm">
          <h2 className="title text-4xl md:text-5xl">
            {bn.title[0]}<span className="text-tang">{bn.title[1]}</span>
          </h2>
          <p className="desc mt-2 text-grape-night/80">{bn.p}</p>
          <Link to="/matching" className="btn mt-4">{bn.btn}</Link>
        </div>
        <img src="/pets/happy-pets.webp" alt={bn.alt} className="mt-6 w-full max-w-md self-center object-contain md:mt-0 md:max-w-[420px]" />
      </div>
    </section>
  )
}

export default function Home() {
  return (
    <>
      <Hero />
      <About />
      <Categories />
      <Voices />
      <Parcours />
      <Banner />
    </>
  )
}
