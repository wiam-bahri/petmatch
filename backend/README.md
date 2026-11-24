# PetMatch Algeria — Backend

API FastAPI pour le catalogue, les profils d'adoptants, le matching PetMatch, les commentaires et les actions administrateur.

## Stack
Python · FastAPI · Uvicorn · Pydantic · SQLAlchemy · SQLite/PostgreSQL · Joblib · pandas · NumPy · SciPy · scikit-learn · XGBoost

## Installation locale
Depuis `backend/` :
```bash
python -m venv .venv
```

Activation :
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# Linux/macOS
source .venv/bin/activate
```

Installer et démarrer :
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Documentation Swagger : `http://127.0.0.1:8000/docs`.

Pour les routes administrateur, définir `ADMIN_KEY` avant le lancement et envoyer la valeur dans l'en-tête `X-Admin-Key`.

## Routes principales
| Méthode | Route | Fonction |
|---|---|---|
| GET | `/api/health` | état de l'API et du modèle |
| GET | `/api/races` | races disponibles par espèce |
| GET | `/api/animals` | liste du catalogue |
| GET | `/api/animals/{id}` | détail animal |
| POST | `/api/match` | calcul des recommandations Top 5 |
| GET / POST | `/api/comments` | consultation et ajout de commentaires |
| POST / DELETE | `/api/animals` et `/api/animals/{id}` | gestion du catalogue (admin) |
| GET | `/api/adopters` et `/api/adopters/{id}` | profils enregistrés (admin) |
| GET / POST / DELETE | `/api/admin/comments...` | modération (admin) |

## Matching et fichiers du modèle
- `app/adapter.py` : traduit les champs du questionnaire vers le profil attendu par le moteur.
- `app/engine.py` : charge le modèle Joblib, prépare le catalogue, évalue et classe les animaux.
- `petmatch/` : implémentation du modèle, du matcher et de la configuration métier.
- `models/` : modèle sérialisé et configuration de matching.
- `app/catalog.py` et `app/seed.py` : catalogue initial et insertion si la base est vide.

Les règles et seuils métier sont des hypothèses configurables; elles ne remplacent pas l'avis d'un refuge ou d'un professionnel.

## Base de données
SQLite est utilisée par défaut en local. `DATABASE_URL` permet de connecter PostgreSQL; les URL PostgreSQL sont normalisées vers le pilote psycopg. Pour une production avec stockage éphémère, utilisez une base persistante afin de conserver les commentaires et les profils.

## Variables d'environnement
- `ADMIN_KEY` : clé requise pour les endpoints admin.
- `DATABASE_URL` : URL DB (optionnelle, SQLite par défaut).
- `CORS_ORIGINS` : origines autorisées, localhost frontend par défaut.
- `COMMENTS_AUTO_APPROVE` : `true` par défaut; `false` active la modération préalable.
- `COMMENTS_PER_HOUR` : limite de commentaires, 5 par défaut.
- `IP_SALT` : secret utilisé pour hash IP; définissez-le en production.

## Tests
```bash
pytest
```
