import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { postMatch } from '../lib/api.js'
import { WILAYAS } from '../lib/data.js'
import { useLang } from '../i18n/LangContext.jsx'

const field = 'w-full rounded-2xl border-2 border-transparent bg-white px-4 py-2 font-alex text-sm text-grape-night focus:border-sun'
const label = 'mb-1 block font-baloo text-sm font-bold'
const err = 'mt-1 font-alex text-[11px] text-sun'

export default function Match() {
  const { t } = useLang()
  const m = t.match
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues: { logement: 'appartement', jardin: 'non', enfants: 'non', experience: 'aucune', wilaya: 'Alger' },
  })
  const [res, setRes] = useState(null)

  const onSubmit = async (values) => setRes(await postMatch(values))

  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="title text-5xl">{m.title[0]}<span className="text-sun">{m.title[1]}</span></h1>
      <p className="desc mt-3 max-w-lg text-white/85">{m.desc}</p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1.1fr]">
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid h-fit content-start gap-4 rounded-[36px] bg-grape-soft p-6 sm:grid-cols-2">
          <div>
            <label className={label} htmlFor="logement">{m.housing}</label>
            <select id="logement" className={field} {...register('logement')}>
              <option value="appartement">{m.apartment}</option>
              <option value="maison">{m.house}</option>
            </select>
          </div>
          <div>
            <label className={label} htmlFor="surface">{m.surface}</label>
            <input id="surface" type="number" className={field} {...register('surface', { required: m.eSurface, min: { value: 10, message: m.eMin } })} />
            {errors.surface && <p className={err} role="alert">{errors.surface.message}</p>}
          </div>
          <div>
            <label className={label} htmlFor="jardin">{m.garden}</label>
            <select id="jardin" className={field} {...register('jardin')}>
              <option value="non">{m.no}</option>
              <option value="oui">{m.yes}</option>
            </select>
          </div>
          <div>
            <label className={label} htmlFor="enfants">{m.kids}</label>
            <select id="enfants" className={field} {...register('enfants')}>
              <option value="non">{m.no}</option>
              <option value="oui">{m.yes}</option>
            </select>
          </div>
          <div>
            <label className={label} htmlFor="experience">{m.experience}</label>
            <select id="experience" className={field} {...register('experience')}>
              <option value="aucune">{m.none}</option>
              <option value="oui">{m.yes}</option>
            </select>
          </div>
          <div>
            <label className={label} htmlFor="temps">{m.time}</label>
            <input id="temps" type="number" step="0.5" className={field} {...register('temps', { required: m.eTime, min: { value: 0, message: m.eInvalid } })} />
            {errors.temps && <p className={err} role="alert">{errors.temps.message}</p>}
          </div>
          <div>
            <label className={label} htmlFor="budget">{m.budget}</label>
            <input id="budget" type="number" className={field} {...register('budget', { required: m.eBudget, min: { value: 0, message: m.eInvalid } })} />
            {errors.budget && <p className={err} role="alert">{errors.budget.message}</p>}
          </div>
          <div>
            <label className={label} htmlFor="wilaya">{m.wilaya}</label>
            <select id="wilaya" className={field} {...register('wilaya')}>
              {WILAYAS.map((w, i) => <option key={w} value={w}>{t.wilayas[i]}</option>)}
            </select>
          </div>
          <div className="sm:col-span-2">
            <button type="submit" disabled={isSubmitting} className="btn w-full disabled:opacity-60">
              {isSubmitting ? m.submitting : m.submit}
            </button>
          </div>
        </form>

        <div className="rounded-[36px] bg-grape-deep p-6">
          {!res ? (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center text-center">
              <img src="/pets/dog-friends.png" alt="" className="h-36 object-contain" />
              <p className="desc mt-4 max-w-xs text-white/80">{m.placeholder}</p>
            </div>
          ) : (
            <>
              <h2 className="title text-3xl">{m.top[0]}<span className="text-sun">{m.top[1]}</span></h2>
              {res.source === 'demo' && (
                <p className="desc mt-1 text-[11px] text-sun">{m.demo}</p>
              )}
              <ol className="mt-4 space-y-3">
                {res.resultats.map((r, i) => (
                  <li key={r.id} className="flex items-center gap-3 rounded-2xl bg-white/10 p-2 pr-4">
                    <span className="h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-sun">
                      <img src={r.img} alt="" className="h-full w-full object-cover object-top" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-baloo font-bold leading-tight">{i + 1}. {r.nom}</p>
                      <p className="desc truncate text-[11px] text-white/70">{r.raisons.map((c) => m.reasons[c]).join(' · ')}</p>
                    </div>
                    <span className="title text-2xl text-sun">{r.score}%</span>
                  </li>
                ))}
              </ol>
              <div className="mt-5 h-48" aria-label={m.chart}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={res.resultats} layout="vertical" margin={{ left: 10, right: 10 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis type="category" dataKey="nom" width={70} tick={{ fill: '#fff', fontFamily: 'Alexandria', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip cursor={false} formatter={(v) => `${v}%`} contentStyle={{ borderRadius: 12, fontFamily: 'Alexandria', fontSize: 12 }} />
                    <Bar dataKey="score" radius={[0, 12, 12, 0]}>
                      {res.resultats.map((r, i) => <Cell key={r.id} fill={['#FFD83D', '#5BD38B', '#FF8DB7', '#3D8BFF', '#FFA24A'][i % 5]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  )
}
