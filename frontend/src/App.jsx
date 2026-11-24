import { Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar.jsx'
import Footer from './components/Footer.jsx'
import Home from './pages/Home.jsx'
import Animals from './pages/Animals.jsx'
import AnimalDetail from './pages/AnimalDetail.jsx'
import Match from './pages/Match.jsx'
import Reviews from './pages/Reviews.jsx'
import Credits from './pages/Credits.jsx'
import Contact from './pages/Contact.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  const location = useLocation()
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const targets = document.querySelectorAll('main section, main li, main article')
    targets.forEach((el) => el.classList.add('scroll-reveal'))
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('scroll-reveal-visible')
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: 0.12, rootMargin: '0px 0px -35px 0px' })
    targets.forEach((el, index) => {
      el.style.setProperty('--reveal-delay', `${Math.min(index % 6, 5) * 55}ms`)
      observer.observe(el)
    })
    return () => observer.disconnect()
  }, [location.pathname])
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/animaux" element={<Animals />} />
          <Route path="/animaux/:id" element={<AnimalDetail />} />
          <Route path="/matching" element={<Match />} />
          <Route path="/avis" element={<Reviews />} />
          <Route path="/credits" element={<Credits />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
