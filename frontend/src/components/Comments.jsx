import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { getComments, postComment } from '../lib/api.js'
import { useLang } from '../i18n/LangContext.jsx'

const field = 'w-full rounded-2xl border-2 border-transparent bg-white px-4 py-2 font-alex text-sm text-grape-night focus:border-sun'
const label = 'mb-1 block font-baloo text-sm font-bold'
const err = 'mt-1 font-alex text-[11px] text-sun'

function Stars({ n, text }) {
  return (
    <span role="img" aria-label={text} className="text-sun">
      {'★'.repeat(n)}<span className="text-white/25">{'★'.repeat(5 - n)}</span>
    </span>
  )
}

// Commentaires RÉELS écrits par les visiteurs (stockés dans SQLite via l'API).
// animalId = commentaires d'un animal ; sans animalId = commentaires généraux du site.
export default function Comments({ animalId }) {
  const { t, lang } = useLang()
  const c = t.comments
  const [items, setItems] = useState([])
  const [state, setState] = useState('loading') // loading | ok | down
  const [notice, setNotice] = useState(null)     // { kind: 'ok' | 'error', text }
  const { register, handleSubmit, reset, watch, formState: { errors, isSubmitting } } = useForm({ defaultValues: { auteur: '', message: '', note: '', site: '' } })
  const len = (watch('message') || '').length

  useEffect(() => {
    let alive = true
    setState('loading')
    getComments({ animalId }).then((d) => { if (alive) { setItems(d); setState('ok') } }).catch(() => alive && setState('down'))
    return () => { alive = false }
  }, [animalId])

  async function onSubmit(v) {
    setNotice(null)
    try {
      const saved = await postComment({ animal_id: animalId ?? null, auteur: v.auteur, message: v.message, note: v.note ? Number(v.note) : null, site: v.site })
      if (saved.approved) setItems((prev) => [saved, ...prev])
      setNotice({ kind: 'ok', text: saved.approved ? c.ok : c.pending })
      reset()
    } catch (e) {
      const status = e.response?.status
      const detail = JSON.stringify(e.response?.data?.detail || '')
      const text = !status ? c.eNet : status === 429 ? c.eRate : status === 422 && /lien/i.test(detail) ? c.eLinks : status === 422 || status === 400 ? c.eMsg : c.eNet
      setNotice({ kind: 'error', text })
    }
  }

  return (
    <div>
      {state === 'loading' && <p className="desc text-white/70">{c.loading}</p>}
      {state === 'down' && <p className="desc text-white/70" role="alert">{c.unavailable}</p>}
      {state === 'ok' && items.length === 0 && <p className="desc text-white/80">{c.none}</p>}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="mt-6 grid gap-4 rounded-[28px] bg-grape-soft p-5 sm:grid-cols-2">
        <h3 className="title text-xl sm:col-span-2">{c.formTitle}</h3>
        <div>
          <label className={label} htmlFor={`auteur-${animalId ?? 'g'}`}>{c.name}</label>
          <input id={`auteur-${animalId ?? 'g'}`} maxLength={40} autoComplete="name" className={field}
            {...register('auteur', { required: c.eName, minLength: { value: 2, message: c.eName } })} />
          {errors.auteur && <p className={err} role="alert">{errors.auteur.message}</p>}
        </div>
        <div>
          <label className={label} htmlFor={`note-${animalId ?? 'g'}`}>{c.rating}</label>
          <select id={`note-${animalId ?? 'g'}`} className={field} {...register('note')}>
            <option value="">{c.noRating}</option>
            {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{'★'.repeat(n)} — {c.stars(n)}</option>)}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className={label} htmlFor={`message-${animalId ?? 'g'}`}>{c.message}</label>
          <textarea id={`message-${animalId ?? 'g'}`} rows={4} maxLength={600} className={field}
            {...register('message', { required: c.eMsg, minLength: { value: 5, message: c.eMsg } })} />
          <div className="flex justify-between gap-3">
            {errors.message ? <p className={err} role="alert">{errors.message.message}</p> : <span />}
            <span className="desc text-[11px] text-white/60">{c.count(len)}</span>
          </div>
        </div>
        {/* Champ piège anti-robots : invisible pour les humains */}
        <div aria-hidden="true" className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
          <label>Site <input tabIndex={-1} autoComplete="off" {...register('site')} /></label>
        </div>
        <div className="flex flex-wrap items-center gap-4 sm:col-span-2">
          <button type="submit" disabled={isSubmitting} className="btn btn-sm disabled:opacity-60">{isSubmitting ? c.sending : c.send}</button>
          {notice && (
            <p role={notice.kind === 'error' ? 'alert' : 'status'} className="desc font-semibold text-grape-night">{notice.kind === 'ok' ? '✓ ' : '⚠ '}{notice.text}</p>
          )}
        </div>
        <p className="desc text-[11px] text-white/60 sm:col-span-2">{c.real}</p>
      </form>

      {items.length > 0 && (
        <div className="comments-list-scroll mt-5" aria-label="Comments list">
          <ul className="grid gap-3">
            {items.map((it) => (
              <li key={it.id} className="rounded-3xl bg-grape-deep p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-baloo text-sm font-bold text-sun">{it.auteur}</p>
                  <p className="desc text-[11px] text-white/50">{new Date(it.created_at).toLocaleDateString(lang)}</p>
                </div>
                {it.note ? <Stars n={it.note} text={c.stars(it.note)} /> : null}
                <p className="desc mt-1 whitespace-pre-line break-words text-white/90">{it.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
