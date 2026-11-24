import { describe, it, expect } from 'vitest'
import { readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'
import credits from './credits.json'
import { ANIMALS } from './data.js'

const ROOT = join(process.cwd(), 'public', 'animals')
const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]))
const photos = walk(ROOT).map((p) => '/animals' + p.slice(ROOT.length).replaceAll('\\', '/'))

describe('crédits des photos (licences Creative Commons)', () => {
  it('chaque photo du dossier public/animals a un auteur, une licence et une page source', () => {
    for (const p of photos) {
      expect(credits[p], `crédit manquant pour ${p}`).toBeTruthy()
      expect(credits[p].author && credits[p].license && credits[p].source).toBeTruthy()
    }
  })
  it('chaque entrée de credits.json correspond à un fichier existant', () => {
    for (const k of Object.keys(credits)) expect(photos).toContain(k)
  })
  it('les animaux de démonstration pointent vers des photos existantes', () => {
    for (const a of ANIMALS) expect(photos).toContain(a.img)
  })
})
