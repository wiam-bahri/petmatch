// Score de compatibilité de démonstration (0–100 %), en attendant model.pkl côté FastAPI.
export function scoreAnimal(profil, animal) {
  let s = 100
  const raisons = []
  const surface = Number(profil.surface) || 0
  const temps = Number(profil.temps) || 0
  const budget = Number(profil.budget) || 0

  if (animal.taille === 'grande' && (profil.logement === 'appartement' || surface < 60)) {
    s -= 30; raisons.push('bigSmall')
  }
  if (animal.energie >= 4 && temps < 2) {
    s -= 25; raisons.push('energyTime')
  }
  if (animal.energie >= 4 && profil.jardin === 'oui') s += 0
  if (animal.energie <= 2 && temps >= 3) { s -= 5 }
  if (animal.espece === 'chien' && profil.experience === 'aucune' && animal.energie >= 4) {
    s -= 15; raisons.push('firstDog')
  }
  if (budget && budget < 3000) { s -= 10; raisons.push('budget') }
  if (animal.age <= 1 && profil.enfants === 'oui' && animal.espece !== 'lapin') s += 0
  if (!raisons.length) raisons.push('good')
  return { id: animal.id, nom: animal.nom, espece: animal.espece, img: animal.img, score: Math.max(0, Math.min(100, s)), raisons }
}

export function scoreAnimals(profil, animals) {
  return animals
    .map((a) => scoreAnimal(profil, a))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
}
