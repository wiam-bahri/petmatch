import Comments from '../components/Comments.jsx'
import { useLang } from '../i18n/LangContext.jsx'

export default function Reviews() {
  const { t } = useLang()
  const r = t.reviewsPage
  return (
    <section className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="title text-5xl">{r.title[0]}<span className="text-sun">{r.title[1]}</span></h1>
      <p className="desc mt-3 max-w-lg text-white/85">{r.desc}</p>
      <div className="mt-8"><Comments /></div>
    </section>
  )
}
