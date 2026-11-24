import axios from 'axios'
import { ANIMALS } from './data.js'
import { scoreAnimals } from './score.js'

// FastAPI (Uvicorn) : en dev le proxy Vite redirige /api vers http://127.0.0.1:8000
export const api = axios.create({ baseURL: '/api', timeout: 6000 })

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
