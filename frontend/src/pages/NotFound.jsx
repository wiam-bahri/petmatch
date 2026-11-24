import { Link } from 'react-router-dom'
import { useLang } from '../i18n/LangContext.jsx'

export default function NotFound() {
  const { t } = useLang()
  return (
    <section className="mx-auto flex max-w-xl flex-col items-center px-5 py-20 text-center">
      <img src="/pets/dog-paw.png" alt="" className="h-52" />
      <h1 className="title mt-4 text-5xl">{t.notFound.title}</h1>
      <p className="desc mt-3 text-white/80">{t.notFound.p}</p>
      <Link to="/" className="btn mt-6">{t.notFound.btn}</Link>
    </section>
  )
}
