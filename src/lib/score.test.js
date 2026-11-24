import { describe, it, expect } from 'vitest'
import { scoreAnimal, scoreAnimals } from './score.js'
import { ANIMALS } from './data.js'

describe('score de compatibilité', () => {
  it('pénalise un grand chien en petit appartement', () => {
    const rex = ANIMALS.find((a) => a.nom === 'Rex')
    const r = scoreAnimal({ logement: 'appartement', surface: 40, temps: 3, budget: 6000, experience: 'oui' }, rex)
    expect(r.score).toBeLessThan(80)
  })
  it('renvoie au plus 5 résultats triés', () => {
    const r = scoreAnimals({ logement: 'maison', surface: 120, temps: 4, budget: 8000, experience: 'oui' }, ANIMALS)
    expect(r.length).toBeLessThanOrEqual(5)
    expect(r[0].score).toBeGreaterThanOrEqual(r[r.length - 1].score)
  })
})
