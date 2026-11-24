import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getAnimals } from '../lib/api.js'
import { ESPECES } from '../lib/data.js'
import { useLang } from '../i18n/LangContext.jsx'

const BG = ['bg-mint', 'bg-sun', 'bg-bubble', 'bg-sky', 'bg-[#FFA24A]', 'bg-grape-soft']

export default function Animals() {
  const { t } = useLang()
  const an = t.animals
  const [params, setParams] = useSearchParams()
  const espece = params.get('espece') || 'tous'
  const [animals, setAnimals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { getAnimals().then((d) => { setAnimals(d); setLoading(false) }) }, [])
  const list = useMemo(() => (espece === 'tous' ? animals : animals.filter((a) => a.espece === espece)), [animals, espece])

  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="title text-5xl">{an.title[0]}<span className="text-sun">{an.title[1]}</span></h1>
      <p className="desc mt-3 max-w-lg text-white/85">{an.desc}</p>

      <div className="mt-6 flex flex-wrap gap-2" role="group" aria-label={an.filter}>
        {ESPECES.map((e) => (
          <button
            key={e.value}
            onClick={() => setParams(e.value === 'tous' ? {} : { espece: e.value })}
            aria-pressed={espece === e.value}
            className={`rounded-full px-5 py-1 font-baloo text-sm font-bold transition ${espece === e.value ? 'bg-sun text-grape-night' : 'bg-white/15 hover:bg-white/25'}`}
          >
            {an.species[e.value]}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="desc mt-10">{an.loading}</p>
      ) : list.length === 0 ? (
        <p className="desc mt-10">{an.empty}</p>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((a, i) => (
            <article key={a.id} className="overflow-hidden rounded-[30px] bg-grape-deep">
              <div className={`relative h-52 ${BG[i % BG.length]}`}>
                <img src={a.img} alt={`${a.nom}, ${an.species[a.espece]}`} className="absolute bottom-0 left-1/2 h-[92%] max-w-none -translate-x-1/2 object-contain" />
              </div>
              <div className="p-5">
                <h2 className="title text-2xl">{a.nom}</h2>
                <p className="desc mt-1 text-white/80">{an.line(an.age(a.age), an.sizes[a.taille], a.energie)}</p>
                <p className="desc text-white/60">{a.wilaya} — {a.asso}</p>
                <Link to="/matching" className="btn btn-sm mt-4">{an.test}</Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
