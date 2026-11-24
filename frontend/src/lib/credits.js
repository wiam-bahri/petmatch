import credits from './credits.json'

// Liens vers le texte des licences Creative Commons (attribution obligatoire pour la plupart des photos)
const LICENSE_URL = {
  'CC BY 2.5': 'https://creativecommons.org/licenses/by/2.5/',
  'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0/',
  'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/',
  'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0/',
  'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/',
  'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
  CC0: 'https://creativecommons.org/publicdomain/zero/1.0/',
}

export const licenseUrl = (name) => LICENSE_URL[name] || null
export const creditFor = (img) => credits[img] || null
export const allCredits = () => Object.entries(credits).map(([img, c]) => ({ img, ...c }))
