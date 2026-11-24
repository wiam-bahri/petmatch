import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getAnimal } from '../lib/api.js'
import { creditFor } from '../lib/credits.js'
import AnimalPhoto from '../components/AnimalPhoto.jsx'
import Comments from '../components/Comments.jsx'
import { useLang } from '../i18n/LangContext.jsx'

export default function AnimalDetail() {
  const { id } = useParams()
  const { t } = useLang()
  const an = t.animals
  const ap = t.animalPage
  const [animal, setAnimal] = useState(undefined) // undefined = chargement, null = introuvable

  useEffect(() => { setAnimal(undefined); getAnimal(id).then(setAnimal) }, [id])

  if (animal === undefined) return <p className="desc mx-auto max-w-6xl px-4 py-12">{ap.loading}</p>
  if (animal === null) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-12">
        <p className="desc">{ap.notFound}</p>
        <Link to="/animaux" className="btn btn-sm mt-4">{ap.back}</Link>
      </section>
    )
  }
  const credit = creditFor(animal.img)
  const facts = [
    [ap.breed, animal.race],
    [ap.age, an.age(animal.age)],
    [ap.size, an.sizes[animal.taille]],
    [ap.energy, `${animal.energie}/5`],
    [ap.place, animal.wilaya],
    [ap.asso, animal.asso],
  ].filter(([, v]) => v)

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <Link to="/animaux" className="desc text-sun hover:underline">{ap.back}</Link>
      <div className="mt-4 grid gap-8 md:grid-cols-2">
        <figure>
          <AnimalPhoto src={animal.img} alt={`${animal.nom}, ${an.species[animal.espece]}`} espece={animal.espece} className="h-72 w-full rounded-[36px] md:h-[420px]" />
          {credit && (
            <figcaption className="desc mt-2 text-[11px] text-white/60">
              {ap.photo} · {credit.author} ·{' '}
              <a href={credit.source} target="_blank" rel="noreferrer" className="underline hover:text-sun">{credit.license}</a>
            </figcaption>
          )}
        </figure>
        <div>
          <p className="desc text-sun">{an.species[animal.espece]}</p>
          <h1 className="title text-5xl">{animal.nom}</h1>
          <dl className="mt-5 grid grid-cols-2 gap-3">
            {facts.map(([k, v]) => (
              <div key={k} className="rounded-2xl bg-grape-deep px-4 py-3">
                <dt className="desc text-[11px] text-white/60">{k}</dt>
                <dd className="font-baloo text-base font-bold">{v}</dd>
              </div>
            ))}
          </dl>
          <Link to="/matching" className="btn mt-6">{ap.test}</Link>
        </div>
      </div>

      <div className="mt-12 max-w-3xl">
        <h2 className="title text-3xl">{ap.commentsTitle(animal.nom)}</h2>
        <div className="mt-4"><Comments animalId={animal.id} /></div>
      </div>
    </section>
  )
}
