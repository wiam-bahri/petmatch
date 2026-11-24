"""PetMatch Algeria — API FastAPI.   Lancer :  uvicorn app.main:app --reload --port 8000   (docs : /docs)"""
import hashlib
import os
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

from .adapter import to_model_profile
from .db import Base, SessionLocal, engine as db_engine, get_db
from .engine import engine
from .models import Adopter, Animal, Comment
from .schemas import AdopterOut, AnimalIn, AnimalOut, CommentIn, CommentOut, MatchItem, ProfilIn
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(db_engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        engine.load()                 # model.pkl chargé une seule fois
        engine.set_catalog(db)
    yield


app = FastAPI(title="PetMatch Algeria API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
                   allow_methods=["*"], allow_headers=["*"])


def admin_only(x_admin_key: str | None = Header(default=None)):
    """Actions réservées à l'admin : en-tête X-Admin-Key == variable d'environnement ADMIN_KEY.
    Si ADMIN_KEY n'est pas définie, ces routes sont FERMÉES (jamais ouvertes par défaut)."""
    key = os.getenv("ADMIN_KEY")
    if not key:
        raise HTTPException(403, "ADMIN_KEY non définie sur le serveur : action admin désactivée.")
    if x_admin_key != key:
        raise HTTPException(401, "Clé admin invalide.")


# ───────────────────────────── Santé ─────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": engine.model is not None, "animals": len(engine.animals)}


# ───────────────────────────── Animaux ─────────────────────────────
def _with_counts(db: Session, rows: list[Animal]) -> list[AnimalOut]:
    counts = dict(db.query(Comment.animal_id, func.count(Comment.id))
                  .filter(Comment.approved.is_(True), Comment.animal_id.isnot(None))
                  .group_by(Comment.animal_id).all())
    return [AnimalOut.model_validate(r).model_copy(update={"nb_commentaires": counts.get(r.id, 0)}) for r in rows]


@app.get("/api/races")
def races():
    """Races acceptées par le modèle, par espèce (pour le formulaire d'ajout d'animal)."""
    return engine.races


@app.get("/api/animals", response_model=list[AnimalOut])
def animals(db: Session = Depends(get_db)):
    return _with_counts(db, db.query(Animal).order_by(Animal.id).all())


@app.get("/api/animals/{animal_id}", response_model=AnimalOut)
def animal(animal_id: int, db: Session = Depends(get_db)):
    row = db.get(Animal, animal_id)
    if not row:
        raise HTTPException(404, "Animal introuvable.")
    return _with_counts(db, [row])[0]


@app.post("/api/animals", response_model=AnimalOut, status_code=201, dependencies=[Depends(admin_only)])
def add_animal(a: AnimalIn, db: Session = Depends(get_db)):
    if a.race not in engine.races.get(a.espece, []):
        raise HTTPException(422, f"Race inconnue pour « {a.espece} ». Voir GET /api/races.")
    data = a.model_dump()
    data["cost_dzd"] = data["cost_dzd"] or float(engine.cost[a.race])
    row = Animal(**data)
    db.add(row); db.commit()
    engine.set_catalog(db)
    return AnimalOut.model_validate(row)


@app.delete("/api/animals/{animal_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    row = db.get(Animal, animal_id)
    if not row:
        raise HTTPException(404, "Animal introuvable.")
    db.query(Comment).filter(Comment.animal_id == animal_id).delete()
    db.delete(row); db.commit()
    engine.set_catalog(db)


# ───────────────────────────── Matching ─────────────────────────────
@app.post("/api/match", response_model=list[MatchItem])
def match(profil: ProfilIn, db: Session = Depends(get_db)):
    if engine.model is None or not engine.animals:
        raise HTTPException(503, "Modèle non chargé ou aucun animal en base.")
    pm = to_model_profile(profil)
    res = engine.rank(pm, k=5)
    db.add(Adopter(profil=profil.model_dump(), profil_modele=pm, resultats=res))
    db.commit()
    return res


@app.get("/api/adopters", response_model=list[AdopterOut], dependencies=[Depends(admin_only)])
def adopters(db: Session = Depends(get_db)):
    """Profils des adoptants (données personnelles -> réservé à l'admin)."""
    return db.query(Adopter).order_by(Adopter.id.desc()).limit(100).all()


@app.get("/api/adopters/{adopter_id}", response_model=AdopterOut, dependencies=[Depends(admin_only)])
def adopter(adopter_id: int, db: Session = Depends(get_db)):
    a = db.get(Adopter, adopter_id)
    if not a:
        raise HTTPException(404, "Adoptant introuvable.")
    return a


# ───────────────────────────── Commentaires (réels, envoyés par les visiteurs) ─────────────────────────────
def _ip_hash(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() or (request.client.host if request.client else "?")
    return hashlib.sha256((os.getenv("IP_SALT", "petmatch") + ip).encode()).hexdigest()[:16]


@app.get("/api/comments", response_model=list[CommentOut])
def list_comments(animal_id: int | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                  db: Session = Depends(get_db)):
    """Commentaires publiés, du plus récent au plus ancien. Sans animal_id : commentaires généraux du site."""
    q = db.query(Comment).filter(Comment.approved.is_(True))
    q = q.filter(Comment.animal_id == animal_id) if animal_id is not None else q.filter(Comment.animal_id.is_(None))
    return q.order_by(Comment.created_at.desc(), Comment.id.desc()).offset(offset).limit(limit).all()


@app.post("/api/comments", response_model=CommentOut, status_code=201)
def post_comment(c: CommentIn, request: Request, db: Session = Depends(get_db)):
    if c.site:                                   # champ piège rempli = robot
        raise HTTPException(400, "Spam détecté.")
    if c.animal_id is not None and not db.get(Animal, c.animal_id):
        raise HTTPException(404, "Animal introuvable.")
    ip = _ip_hash(request)
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(tzinfo=None)
    recent = db.query(func.count(Comment.id)).filter(Comment.ip_hash == ip, Comment.created_at >= since).scalar()
    if recent >= int(os.getenv("COMMENTS_PER_HOUR", "5")):
        raise HTTPException(429, "Trop de commentaires, réessayez plus tard.")
    auto = os.getenv("COMMENTS_AUTO_APPROVE", "true").lower() != "false"      # false = modération préalable
    row = Comment(animal_id=c.animal_id, auteur=c.auteur, message=c.message, note=c.note, approved=auto, ip_hash=ip)
    db.add(row); db.commit()
    return row


@app.get("/api/admin/comments", response_model=list[CommentOut], dependencies=[Depends(admin_only)])
def admin_comments(status: str = "pending", db: Session = Depends(get_db)):
    """status=pending (à valider) | all."""
    q = db.query(Comment)
    if status == "pending":
        q = q.filter(Comment.approved.is_(False))
    return q.order_by(Comment.created_at.desc()).limit(200).all()


@app.post("/api/admin/comments/{comment_id}/approve", response_model=CommentOut, dependencies=[Depends(admin_only)])
def approve_comment(comment_id: int, db: Session = Depends(get_db)):
    row = db.get(Comment, comment_id)
    if not row:
        raise HTTPException(404, "Commentaire introuvable.")
    row.approved = True
    db.commit()
    return row


@app.delete("/api/admin/comments/{comment_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    row = db.get(Comment, comment_id)
    if not row:
        raise HTTPException(404, "Commentaire introuvable.")
    db.delete(row); db.commit()


# ───────────────────────────── Site React (front) servi par FastAPI ─────────────────────────────
# Un seul service Render : /api/* = backend, tout le reste = fichiers du build React (frontend/dist).
# À laisser TOUT EN BAS du fichier : cette route « attrape-tout » doit venir après les routes /api.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (DIST / "index.html").is_file():
    if (DIST / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(404, "Route API introuvable.")
        f = (DIST / full_path).resolve()
        if full_path and f.is_file() and DIST.resolve() in f.parents:   # favicon, polices, photos...
            return FileResponse(f)
        return FileResponse(DIST / "index.html")                         # React Router gère le reste
