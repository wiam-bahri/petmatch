import { Link } from 'react-router-dom'
import { Paw } from './Icons.jsx'
import { useLang } from '../i18n/LangContext.jsx'

export default function Footer() {
  const { t } = useLang()
  const f = t.footer
  return (
    <footer id="contact" className="bg-grape-night">
      <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2 text-sun">
            <Paw className="h-8 w-8" />
            <span className="font-baloo text-2xl font-extrabold">PetMatch Algeria</span>
          </div>
          <p className="desc mt-3 max-w-xs text-white/75">{f.desc}</p>
        </div>
        <div>
          <h3 className="font-baloo text-lg font-bold text-sun">{f.explore}</h3>
          <ul className="desc mt-2 space-y-1 text-white/80">
            <li><Link to="/animaux" className="hover:text-sun">{f.animals}</Link></li>
            <li><Link to="/matching" className="hover:text-sun">{f.form}</Link></li>
            <li><Link to="/avis" className="hover:text-sun">{f.reviews}</Link></li>
            <li><Link to="/credits" className="hover:text-sun">{f.credits}</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="font-baloo text-lg font-bold text-sun">{f.partners}</h3>
          <ul className="desc mt-2 space-y-1 text-white/80">
            <li>El Rifk</li>
            <li>LPAA</li>
          </ul>
        </div>
      </div>
      <p className="desc border-t border-white/10 py-4 text-center text-[11px] text-white/50">{f.uni}</p>
    </footer>
  )
}
