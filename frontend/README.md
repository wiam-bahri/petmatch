# PetMatch Algeria — Frontend

Application web React de PetMatch Algeria, construite avec Vite. Elle présente le catalogue, les fiches animaux, le questionnaire de matching, les avis et les pages informatives. L'interface prend en charge EN / FR / AR avec RTL pour l'arabe.

## Stack
- React 18 et Vite
- Tailwind CSS
- React Router
- React Hook Form
- Axios
- Recharts
- Vitest

## Installation et scripts
```bash
npm install
npm run dev      # serveur local : http://localhost:5173
npm test         # tests Vitest
npm run build    # build de production
npm run preview  # prévisualiser le build local
```

En mode développement, Vite redirige `/api` vers FastAPI sur `http://127.0.0.1:8000`. Lancez le backend séparément pour les données réelles et le matching. Si l'API catalogue/matching est indisponible, le frontend peut utiliser les données et scores de démonstration; les commentaires ne sont pas simulés.

## API
- `GET /api/animals` : catalogue
- `GET /api/animals/{id}` : fiche
- `POST /api/match` : recommandations du modèle
- `GET /api/comments` et `POST /api/comments` : commentaires

La base URL peut être configurée via `VITE_API_URL` selon l'environnement. Pour Vercel, vérifiez la destination des rewrites dans `vercel.json` et remplacez toute URL API ancienne par celle du backend actuel.

## Langues et styles
Les traductions se trouvent dans `src/i18n/translations.js`. Le choix de langue est géré par le contexte de langue. L'arabe utilise une direction RTL. Les polices et styles sont configurés dans les fichiers CSS de l'application.

## Ressources visuelles
Les images statiques sont servies depuis `public/`. Les images optimisées WebP de certaines sections d'accueil sont dans `public/pets/`. Consultez les crédits et licences des photos avant toute redistribution.
