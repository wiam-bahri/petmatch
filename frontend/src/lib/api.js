import axios from 'axios'
import { ANIMALS } from './data.js'
import { scoreAnimals } from './score.js'

// FastAPI (Uvicorn) : en dev le proxy Vite redirige /api vers http://127.0.0.1:8000
// VITE_API_URL (ex: https://petmatch-api.onrender.com) = appel direct à Render ; vide = proxy /api (Vite en dev, rewrite Vercel en prod).
// timeout 60 s : Render (offre gratuite) met ~30-50 s à se réveiller ; avec 6 s on retombait toujours sur le mode démo.
export const api = axios.create({ baseURL: `${import.meta.env.VITE_API_URL || ''}/api`, timeout: 60000 })

export async function getAnimals() {
  try {
    const { data } = await api.get('/animals')
    return data
  } catch {
    return ANIMALS // repli démo
  }
}

// Envoie le profil adoptant au modèle ML ; repli sur un score local si l'API est absente.
export async function postMatch(profil) {
  try {
    const { data } = await api.post('/match', profil)
    return { source: 'api', resultats: data }
  } catch {
    return { source: 'demo', resultats: scoreAnimals(profil, ANIMALS) }
  }
}

export async function getAnimal(id) {
  try {
    const { data } = await api.get(`/animals/${id}`)
    return data
  } catch (e) {
    if (e.response?.status === 404) return null
    return ANIMALS.find((a) => a.id === Number(id)) || null // repli démo si l'API est absente
  }
}

// Commentaires : AUCUN repli démo, on n'affiche jamais de faux commentaires (si l'API échoue, l'erreur remonte).
export async function getComments({ animalId, limit = 20 } = {}) {
  const params = { limit }
  if (animalId != null) params.animal_id = animalId
  const { data } = await api.get('/comments', { params })
  return data
}

export async function postComment(body) {
  const { data } = await api.post('/comments', body)
  return data
}
