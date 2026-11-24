import { Link, NavLink } from 'react-router-dom'
import { Paw } from './Icons.jsx'
import LangSwitcher from './LangSwitcher.jsx'
import { useLang } from '../i18n/LangContext.jsx'

export default function Navbar() {
  const { t } = useLang()
  const links = [
    { to: '/', label: t.nav.home, end: true },
    { to: '/animaux', label: t.nav.animals },
    { to: '/matching', label: t.nav.matching },
    { to: '/#contact', label: t.nav.contact, hash: true },
  ]
  return (
    <header className="sticky top-0 z-40 bg-sun text-grape-night">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-4 sm:px-5">
        <Link to="/" className="flex items-center gap-2 text-tang" aria-label={t.nav.brandLabel}>
          <Paw className="h-7 w-7" />
          <span className="font-baloo text-xl font-extrabold text-tang">PetMatch</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex" aria-label={t.nav.main}>
          {links.map((l) =>
            l.hash ? (
              <a key={l.to} href="/#contact" className="font-baloo text-sm font-semibold hover:text-tang">{l.label}</a>
            ) : (
              <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => `font-baloo text-sm font-semibold hover:text-tang ${isActive ? 'text-tang' : ''}`}>
                {l.label}
              </NavLink>
            ),
          )}
        </nav>

        <div className="flex items-center gap-2">
          <LangSwitcher />
          <Link to="/animaux" aria-label={t.nav.seeAnimals} className="hidden h-9 w-9 overflow-hidden rounded-full border-2 border-tang bg-white sm:block">
            <img src="/pets/cat.png" alt="" className="h-full w-full object-cover object-top" />
          </Link>
          <Link to="/matching" aria-label={t.nav.startMatching} className="hidden h-9 w-9 overflow-hidden rounded-full border-2 border-tang bg-white sm:block">
            <img src="/pets/shiba.png" alt="" className="h-full w-full object-cover object-top" />
          </Link>
        </div>
      </div>
      <nav className="flex justify-center gap-5 pb-2 md:hidden" aria-label={t.nav.mobile}>
        {links.filter((l) => !l.hash).map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => `font-baloo text-sm font-semibold ${isActive ? 'text-tang' : ''}`}>
            {l.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
