import { allCredits, licenseUrl } from '../lib/credits.js'
import { useLang } from '../i18n/LangContext.jsx'

export default function Credits() {
  const { t } = useLang()
  const cr = t.credits
  const rows = allCredits().sort((a, b) => a.breed.localeCompare(b.breed))
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="title text-5xl">{cr.title[0]}<span className="text-sun">{cr.title[1]}</span></h1>
      <p className="desc mt-3 max-w-2xl text-white/85">{cr.desc}</p>
      <div className="mt-8 overflow-x-auto rounded-3xl bg-grape-deep">
        <table className="w-full min-w-[640px] text-start">
          <thead>
            <tr className="font-baloo text-sm text-sun">{cr.cols.map((h) => <th key={h} className="px-4 py-3 text-start">{h}</th>)}</tr>
          </thead>
          <tbody className="desc">
            {rows.map((r) => (
              <tr key={r.img} className="border-t border-white/10">
                <td className="px-4 py-2 font-semibold">{r.breed}</td>
                <td className="px-4 py-2 text-white/80">{r.author}</td>
                <td className="px-4 py-2">
                  {licenseUrl(r.license) ? <a href={licenseUrl(r.license)} target="_blank" rel="noreferrer" className="underline hover:text-sun">{r.license}</a> : r.license}
                </td>
                <td className="px-4 py-2"><a href={r.source} target="_blank" rel="noreferrer" className="underline hover:text-sun">{cr.source}</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
