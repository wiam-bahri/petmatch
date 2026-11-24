# PetMatch Algeria 🐾

**PetMatch Algeria** est une plateforme web qui aide les personnes souhaitant adopter un animal à découvrir des animaux disponibles et à identifier ceux qui correspondent le mieux à leur mode de vie. Le projet combine un catalogue d'animaux, un formulaire de matching alimenté par un modèle, des fiches détaillées, des commentaires communautaires et une interface multilingue.

> Le matching est un outil d'aide à la décision : les besoins réels d'un animal doivent toujours être confirmés auprès de l'association, du refuge ou d'un professionnel compétent.

## Fonctionnalités

- **Accueil** : présentation du projet, sections de découverte et témoignages/avis.
- **Catalogue des animaux** : consultation, filtrage et fiches individuelles.
- **Matching** : questionnaire sur le logement, la présence à la maison, le budget, l'expérience, les enfants et les préférences; résultats classés avec un score et des explications.
- **Fiches animaux** : informations et commentaires associés à chaque animal.
- **Avis de la communauté** : commentaires généraux et commentaires sur les animaux, avec contrôle anti-spam et modération configurable.
- **Multilingue** : anglais, français et arabe; l'affichage arabe prend en charge RTL.
- **Administration API** : routes protégées par une clé pour gérer les commentaires et le catalogue.
- **Fallback frontend** : des données et un score de démonstration sont utilisés lorsque certaines requêtes API échouent; les commentaires, eux, ne sont pas simulés.
- **Images optimisées** : les images de la page d'accueil incluent des versions WebP plus légères.

## Technologies

| Partie | Technologies |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, React Hook Form, Axios, Recharts |
| Backend / API | Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy |
| Base de données | SQLite en local par défaut; PostgreSQL possible via `DATABASE_URL` |
| Matching | modèle sérialisé Joblib, pandas, NumPy, SciPy, scikit-learn, XGBoost |
| Tests | Vitest côté frontend; pytest côté backend |
| Déploiement | Docker et Render; frontend déployable séparément si la configuration API est ajustée |

## Architecture

```text
PetMatch Algeria
├── frontend/                 # Application React + Vite
│   ├── src/                  # pages, composants, traductions et logique frontend
│   └── public/                # images, icônes et ressources statiques
├── backend/
│   ├── app/                  # API FastAPI, schémas, DB, seed et adaptateur de profil
│   ├── petmatch/             # moteur de matching et configuration
│   ├── models/               # modèle entraîné et configuration de matching
│   └── tests/                 # tests pytest
├── Dockerfile                # build frontend puis image backend
└── render.yaml                # configuration Render
```

### Flux de matching

1. Le frontend collecte le profil de l'adoptant.
2. Le profil est envoyé à `POST /api/match`.
3. L'adaptateur backend convertit les réponses du formulaire en variables attendues par le modèle.
4. Le moteur évalue les animaux du catalogue, applique les règles et calcule les scores.
5. L'API renvoie les meilleurs résultats avec score, compatibilité et explications.

Le modèle et les fichiers de données d'entraînement ne sont pas modifiés lors de l'utilisation du site. Les règles et paramètres du moteur sont configurés dans le backend.


## Lancer le projet en local

Prérequis : **Python 3.12**, **Node.js 22** recommandé (Node 22 est utilisé dans le Dockerfile), npm.

### 1. Démarrer le backend

Depuis la racine du dépôt :

```bash
cd backend
python -m venv .venv
```

Activation de l'environnement virtuel :

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

Installer les dépendances puis lancer l'API :

```bash
pip install -r requirements.txt

# Linux / macOS
ADMIN_KEY="votre-cle-admin" uvicorn app.main:app --reload --port 8000

# Windows PowerShell
$env:ADMIN_KEY="votre-cle-admin"
uvicorn app.main:app --reload --port 8000
```

API et documentation interactive :
- API : `http://127.0.0.1:8000`
- Swagger : `http://127.0.0.1:8000/docs`
- Santé : `http://127.0.0.1:8000/api/health`

### 2. Démarrer le frontend

Dans un **second terminal**, depuis la racine du dépôt :

```bash
cd frontend
npm install
npm run dev
```

Le frontend est disponible sur `http://localhost:5173`. En développement, le proxy Vite redirige les appels `/api` vers FastAPI sur le port 8000.

### Commandes utiles

```bash
npm run dev       # serveur de développement
npm run build     # build de production
npm run preview   # prévisualiser le build
npm test          # tests frontend (Vitest)
```

Pour le backend :

```bash
pytest            # lancer les tests backend depuis backend/
```

## Pages et routes frontend

| Route | Description |
|---|---|
| `/` | Page d'accueil |
| `/animaux` | Catalogue et filtres |
| `/animaux/:id` | Fiche d'un animal et commentaires associés |
| `/matching` | Questionnaire de profil et recommandations personnalisées |
| `/avis` | Avis/commentaires généraux de la communauté |
| `/credits` | Crédits des photos et sources |
| `/contact` | Page de contact |

## API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | État de l'API, chargement du modèle et nombre d'animaux |
| `GET` | `/api/races` | Races prises en charge par le modèle, par espèce |
| `GET` | `/api/animals` | Liste des animaux avec nombre de commentaires approuvés |
| `GET` | `/api/animals/{animal_id}` | Détails d'un animal |
| `POST` | `/api/match` | Évalue le profil et retourne les recommandations |
| `GET` | `/api/comments` | Commentaires publiés; filtres `animal_id`, `limit`, `offset` |
| `POST` | `/api/comments` | Ajouter un commentaire |
| `POST` | `/api/animals` | Ajouter un animal (admin) |
| `DELETE` | `/api/animals/{animal_id}` | Supprimer un animal (admin) |
| `GET` | `/api/adopters` | Profils enregistrés (admin) |
| `GET` | `/api/adopters/{adopter_id}` | Détail d'un profil enregistré (admin) |
| `GET` | `/api/admin/comments` | Liste de commentaires à modérer ou tous les commentaires (admin) |
| `POST` | `/api/admin/comments/{comment_id}/approve` | Approuver un commentaire (admin) |
| `DELETE` | `/api/admin/comments/{comment_id}` | Supprimer un commentaire (admin) |

Les endpoints administrateur requièrent l'en-tête HTTP `X-Admin-Key`, dont la valeur doit correspondre à `ADMIN_KEY` côté serveur. Si `ADMIN_KEY` n'est pas configurée, les routes administrateur restent fermées.


## Configuration des variables d'environnement

| Variable | Utilité | Valeur / comportement |
|---|---|---|
| `ADMIN_KEY` | Protection des routes admin | À définir; clé secrète non publique |
| `DATABASE_URL` | Connexion base de données | Absente : SQLite local; configurée : URL PostgreSQL acceptée |
| `CORS_ORIGINS` | Origines autorisées par CORS | Par défaut `http://localhost:5173`; plusieurs origines séparées par des virgules |
| `COMMENTS_AUTO_APPROVE` | Publication automatique des commentaires | `true` par défaut; `false` active l'approbation admin préalable |
| `COMMENTS_PER_HOUR` | Limite de commentaires par IP et par heure | `5` par défaut |
| `IP_SALT` | Salt utilisé pour le hash IP | Valeur par défaut prévue pour le développement; définir une valeur secrète en production |
| `PORT` | Port d'écoute du service Docker/Render | Le conteneur utilise `10000` si `PORT` n'est pas fourni |


## Commentaires et modération

- Les commentaires sont envoyés par les visiteurs; aucun faux commentaire n'est préchargé pour l'affichage.
- Longueur acceptée : 5 à 600 caractères; auteur : 2 à 40 caractères.
- Les liens sont refusés; un champ anti-robot (honeypot) est utilisé.
- La limite par défaut est de 5 commentaires par IP hashée sur une heure.
- `COMMENTS_AUTO_APPROVE=false` permet de garder les commentaires en attente d'approbation.
- Les routes de modération utilisent `X-Admin-Key`.
- Le frontend ne simule pas de commentaires si l'API échoue.

## Catalogue, races et images

- Le catalogue initial est défini dans `backend/app/catalog.py` et inséré au démarrage si la base est vide.
- Les races disponibles pour l'ajout d'animaux sont exposées par `GET /api/races` et validées par rapport aux races du modèle.
- Les photos du frontend se trouvent dans `frontend/public/` (notamment les dossiers `animals/` et `pets/`).
- Les crédits et sources des photos sont maintenus dans `frontend/src/lib/credits.json` / les fichiers de crédits du frontend; consultez la page **Credits** avant de redistribuer les images.
- Les versions WebP optimisées de certaines images de la page d'accueil sont conservées dans `public/pets/`; les images originales peuvent rester présentes pour d'autres usages.

## Tests

Frontend :

```bash
cd frontend
npm test
npm run build
```

Backend :

```bash
cd backend
pytest
```

Les tests vérifient notamment le fonctionnement des routes API, des règles de matching et des crédits d'images côté frontend.

## Déploiement sur Render (service complet)

Le dépôt inclut un `Dockerfile` à la racine qui :

1. installe les dépendances frontend et construit l'application Vite;
2. installe les dépendances Python;
3. copie le build frontend dans le backend;
4. démarre Uvicorn, qui sert l'API et l'application React.

Configuration recommandée :
- créer un **Web Service** sur Render;
- choisir le runtime **Docker** et conserver le `Dockerfile` à la racine;
- utiliser le `render.yaml` fourni comme référence de configuration;
- renseigner `ADMIN_KEY` dans les variables d'environnement Render;
- configurer `DATABASE_URL` avec une base PostgreSQL si la persistance des commentaires et profils est nécessaire.

Le health check est `GET /api/health`.

**Important pour la persistance :** la base SQLite locale n'est pas adaptée à un disque éphémère. En environnement Render sans disque/base persistante, les commentaires et profils stockés localement peuvent être perdus lors d'un redéploiement ou du remplacement de l'instance. Utilisez PostgreSQL avec `DATABASE_URL` pour la persistance.

## Déploiement frontend séparé (Vercel)

Le dossier `frontend/` peut être déployé séparément, mais il faut vérifier et mettre à jour la destination API dans `frontend/vercel.json` pour qu'elle pointe vers le backend réellement déployé. Le frontend utilise `/api` et peut aussi être configuré via `VITE_API_URL` selon l'environnement. Ne déployez pas une URL d'API placeholder ou obsolète.

## Sécurité et confidentialité

- Ne publiez jamais `ADMIN_KEY`, les secrets de base de données ou autres variables sensibles dans le dépôt ou le frontend.
- Les profils envoyés au matching sont enregistrés par l'API pour le fonctionnement de l'historique/admin; les endpoints de consultation sont protégés.
- Les adresses IP sont hashées pour le mécanisme de limitation des commentaires; définissez `IP_SALT` en production.
- Vérifiez les licences et les crédits des images avant réutilisation ou redistribution.

## Licence et crédits

Les crédits des photos et les informations de licence sont indiqués dans la page **Credits** du site et dans les fichiers de crédits du frontend. Vérifiez ces informations avant toute réutilisation des ressources visuelles. Le présent dépôt ne présume pas d'une licence globale pour toutes les ressources.


---

Développé pour faciliter la découverte et l'adoption responsable des animaux en Algérie. 🐶🐱
