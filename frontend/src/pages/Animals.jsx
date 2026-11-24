import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getAnimals } from '../lib/api.js'
import { ESPECES } from '../lib/data.js'
import AnimalPhoto from '../components/AnimalPhoto.jsx'
import { useLang } from '../i18n/LangContext.jsx'

const selectClass = 'w-full rounded-2xl border border-white/15 bg-grape-night/70 px-4 py-3 text-white outline-none focus:border-sun'


export default function Animals() {
  const { t } = useLang()
  const an = t.animals
  const [params, setParams] = useSearchParams()
  const espece = params.get('espece') || 'tous'
  const [animals, setAnimals] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [energy, setEnergy] = useState('')
  const [size, setSize] = useState('')
  const [ageGroup, setAgeGroup] = useState('')
  const [wilaya, setWilaya] = useState('')

  useEffect(() => {
    getAnimals().then((d) => { setAnimals(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const locations = useMemo(() => [...new Set(animals.map((a) => a.wilaya).filter(Boolean))].sort(), [animals])
  const activeFilters = [search.trim(), energy, size, ageGroup, wilaya].filter(Boolean).length
  const list = useMemo(() => animals.filter((a) => {
    if (espece !== 'tous' && a.espece !== espece) return false
    if (search.trim() && !`${a.nom} ${a.race || ''} ${a.asso || ''}`.toLowerCase().includes(search.trim().toLowerCase())) return false
    if (energy === 'low' && a.energie > 2) return false
    if (energy === 'medium' && a.energie !== 3) return false
    if (energy === 'high' && a.energie < 4) return false
    if (size && a.taille !== size) return false
    if (ageGroup === 'young' && a.age > 1) return false
    if (ageGroup === 'adult' && (a.age <= 1 || a.age > 7)) return false
    if (ageGroup === 'senior' && a.age <= 7) return false
    if (wilaya && a.wilaya !== wilaya) return false
    return true
  }), [animals, espece, search, energy, size, ageGroup, wilaya])


  const resetFilters = () => {
    setSearch(''); setEnergy(''); setSize(''); setAgeGroup(''); setWilaya('')
    setParams({})
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="title text-5xl">{an.title[0]}<span className="text-sun">{an.title[1]}</span></h1>
      <p className="desc mt-3 max-w-lg text-white/85">{an.desc}</p>

      <div className="mt-6 flex flex-wrap gap-2" role="group" aria-label={an.filter}>
        {ESPECES.map((e) => (
          <button key={e.value} onClick={() => setParams(e.value === 'tous' ? {} : { espece: e.value })}
            aria-pressed={espece === e.value}
            className={`rounded-full px-5 py-2 font-baloo text-sm font-bold transition ${espece === e.value ? 'bg-sun text-grape-night' : 'bg-white/15 hover:bg-white/25'}`}>
            {an.species[e.value]}
          </button>
        ))}
      </div>


      <div className="mt-5 rounded-[28px] border border-white/10 bg-grape-deep/70 p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="title text-xl">{an.advancedTitle}</h2>
            <p className="desc mt-1 text-sm text-white/65">{an.advancedDesc}</p>
          </div>
          <button onClick={resetFilters} className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold transition hover:bg-white/20">
            {an.reset} {activeFilters > 0 && <span className="ml-1 rounded-full bg-sun px-2 text-grape-night">{activeFilters}</span>}
          </button>
        </div>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <label className="block lg:col-span-1"><span className="desc mb-2 block text-xs">{an.searchLabel}</span>
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={an.searchPlaceholder} className={selectClass} /></label>
          <label className="block"><span className="desc mb-2 block text-xs">{an.energyLabel}</span>
            <select value={energy} onChange={(e) => setEnergy(e.target.value)} className={selectClass}><option value="">{an.any}</option><option value="low">{an.energyLow}</option><option value="medium">{an.energyMedium}</option><option value="high">{an.energyHigh}</option></select></label>
          <label className="block"><span className="desc mb-2 block text-xs">{an.sizeLabel}</span>
            <select value={size} onChange={(e) => setSize(e.target.value)} className={selectClass}><option value="">{an.any}</option><option value="petite">{an.sizes.petite}</option><option value="moyenne">{an.sizes.moyenne}</option><option value="grande">{an.sizes.grande}</option></select></label>
          <label className="block"><span className="desc mb-2 block text-xs">{an.ageLabel}</span>
            <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)} className={selectClass}><option value="">{an.any}</option><option value="young">{an.ageYoung}</option><option value="adult">{an.ageAdult}</option><option value="senior">{an.ageSenior}</option></select></label>
          <label className="block"><span className="desc mb-2 block text-xs">{an.locationLabel}</span>
            <select value={wilaya} onChange={(e) => setWilaya(e.target.value)} className={selectClass}><option value="">{an.any}</option>{locations.map((w) => <option key={w} value={w}>{w}</option>)}</select></label>
        </div>
        <div className="mt-4 flex items-center justify-between gap-3 border-t border-white/10 pt-4">
          <p className="desc text-sm">{an.resultsCount(list.length)}</p>
          <span className="text-xs text-white/45">{an.energyHint}</span>
        </div>
      </div>


      {loading ? (
        <p className="desc mt-10">{an.loading}</p>
      ) : list.length === 0 ? (
        <div className="mt-10 rounded-3xl bg-white/5 p-8 text-center"><p className="desc">{an.empty}</p><button onClick={resetFilters} className="btn btn-sm mt-4">{an.reset}</button></div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((a) => (
            <article key={a.id} className="overflow-hidden rounded-[30px] bg-grape-deep">
              <Link to={`/animaux/${a.id}`} aria-label={`${an.details} : ${a.nom}`} className="relative block">
                <AnimalPhoto src={a.img} alt={`${a.nom}, ${an.species[a.espece]}`} espece={a.espece} className="h-52 w-full" />
                <span className="absolute left-3 top-3 rounded-full bg-grape-night/80 px-3 py-0.5 font-baloo text-xs font-bold text-sun">{an.species[a.espece]}</span>
              </Link>
              <div className="p-5">
                <h2 className="title text-2xl">{a.nom}</h2>
                {a.race && <p className="desc text-sun">{a.race}</p>}
                <p className="desc mt-1 text-white/80">{an.line(an.age(a.age), an.sizes[a.taille], a.energie)}</p>
                <p className="desc text-white/60">{a.wilaya} — {a.asso}</p>
                <p className="desc mt-1 text-[11px] text-white/50">💬 {an.nbComments(a.nb_commentaires ?? 0)}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Link to={`/animaux/${a.id}`} className="btn btn-sm">{an.details}</Link>
                  <Link to="/matching" className="btn btn-sm bg-white/15 text-white hover:bg-white/25">{an.test}</Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
