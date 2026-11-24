import os
os.environ["DATABASE_URL"] = "sqlite:///./test_petmatch.db"
os.environ["ADMIN_KEY"] = "secret-test"
os.environ["COMMENTS_PER_HOUR"] = "50"
import pathlib
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.adapter import to_model_profile
from app.schemas import ProfilIn
from app.catalog import CATALOG

ADM = {"X-Admin-Key": "secret-test"}
OK = dict(logement="maison", surface=120, jardin="oui", enfants="non", experience="oui", temps=10, budget=60000, wilaya="Blida")


@pytest.fixture(scope="module")
def c():
    with TestClient(app) as client:
        yield client


def test_adapter():
    p = to_model_profile(ProfilIn(**{**OK, "logement": "appartement", "surface": 50}))
    assert p["Type_Logement"] == "Appartement F3" and p["Nombre_Enfants"] == 0 and p["Experience_Animaux"] == "Intermédiaire"


def test_catalog_is_valid(c):
    """Chaque ligne du catalogue : race connue du modèle + photo présente dans le front (si le dossier existe)."""
    races = c.get("/api/races").json()
    names = [r[0] for r in CATALOG]
    assert len(set(names)) == len(names)
    pub = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "public"
    for nom, esp, race, *_rest, img, _chr, _beh in CATALOG:
        assert race in races[esp], f"{nom}: race {race} inconnue pour {esp}"
        if pub.exists():
            assert (pub / img.lstrip("/")).is_file(), f"{nom}: photo manquante {img}"


def test_animals_and_match(c):
    assert c.get("/api/health").json()["model_loaded"] is True
    a = c.get("/api/animals").json()
    assert len(a) == len(CATALOG) and {"id", "nom", "espece", "race", "taille", "energie", "img", "nb_commentaires"} <= set(a[0])
    assert {x["espece"] for x in a} == {"chat", "chien", "lapin", "oiseau", "poisson", "reptile", "mammifere"}
    res = c.post("/api/match", json=OK).json()
    assert 1 <= len(res) <= 5 and all(0 <= x["score"] <= 100 and x["raisons"] for x in res)
    assert res == sorted(res, key=lambda x: (-x["compatible"], -x["score"]))
    assert c.get("/api/animals/1").json()["id"] == 1 and c.get("/api/animals/9999").status_code == 404


def test_blocked_profile_gives_reasons(c):
    bad = {**OK, "logement": "appartement", "surface": 30, "budget": 500, "temps": 1, "experience": "aucune"}
    res = c.post("/api/match", json=bad).json()
    assert all(not x["compatible"] and x["score"] > 0 for x in res)  # score informatif, décision toujours NON
    assert all(x["raisons"] and "good" not in x["raisons"] for x in res)


def test_validation(c):
    assert c.post("/api/match", json={**OK, "surface": 2}).status_code == 422


def test_admin_routes_are_protected(c):
    assert c.get("/api/adopters").status_code == 401
    assert c.get("/api/adopters", headers=ADM).status_code == 200
    assert c.post("/api/animals", json={}).status_code == 401
    assert c.delete("/api/animals/1").status_code == 401
    assert c.get("/api/admin/comments").status_code == 401


def test_admin_closed_without_key(c, monkeypatch):
    monkeypatch.delenv("ADMIN_KEY")
    assert c.get("/api/adopters", headers=ADM).status_code == 403     # jamais ouvert par défaut


def test_add_and_delete_animal(c):
    new = dict(nom="ZZ-Test", espece="chat", age=2, taille="petite", energie=3, wilaya="Alger", asso="LPAA",
               img="/animals/cats/siamese.jpg", race="Siamese")
    assert c.get("/api/races").json()["oiseau"]
    r = c.post("/api/animals", json=new, headers=ADM)
    assert r.status_code == 201
    aid = r.json()["id"]
    assert c.post("/api/animals", json={**new, "race": "Macaw"}, headers=ADM).status_code == 422     # race d'une autre espèce
    assert c.post("/api/animals", json={**new, "img": "http://x/y.png"}, headers=ADM).status_code == 422
    c.post("/api/comments", json={"animal_id": aid, "auteur": "Sara", "message": "Très beau chat !"})
    assert c.delete(f"/api/animals/{aid}", headers=ADM).status_code == 204
    assert not any(x["nom"] == "ZZ-Test" for x in c.get("/api/animals").json())


# ───────── commentaires ─────────
def test_comments_flow(c):
    assert c.get("/api/comments").json() == []                      # aucun faux commentaire au départ
    r = c.post("/api/comments", json={"animal_id": 1, "auteur": "  Amina ", "message": "Maya est adorable,   très douce.", "note": 5})
    assert r.status_code == 201 and r.json()["auteur"] == "Amina" and r.json()["message"] == "Maya est adorable, très douce."
    assert r.json()["created_at"].endswith(("Z", "+00:00"))
    c.post("/api/comments", json={"auteur": "Karim", "message": "Site très utile pour choisir."})
    assert [x["auteur"] for x in c.get("/api/comments", params={"animal_id": 1}).json()] == ["Amina"]
    assert [x["auteur"] for x in c.get("/api/comments").json()] == ["Karim"]            # général seulement
    assert next(a for a in c.get("/api/animals").json() if a["id"] == 1)["nb_commentaires"] == 1


@pytest.mark.parametrize("payload,code", [
    ({"auteur": "A", "message": "Bonjour tout le monde"}, 422),                       # nom trop court
    ({"auteur": "Ali", "message": "ok"}, 422),                                         # message trop court
    ({"auteur": "Ali", "message": "x" * 601}, 422),                                    # trop long
    ({"auteur": "Ali", "message": "Visitez https://spam.com"}, 422),                   # lien interdit
    ({"auteur": "Ali", "message": "Visitez www.spam.ru maintenant"}, 422),
    ({"auteur": "Ali", "message": "Message correct ici", "note": 9}, 422),             # note hors 1..5
    ({"auteur": "Ali", "message": "Message correct ici", "site": "bot"}, 400),         # honeypot
    ({"auteur": "Ali", "message": "Message correct ici", "animal_id": 9999}, 404),
])
def test_comment_rejections(c, payload, code):
    assert c.post("/api/comments", json=payload).status_code == code


def test_comment_html_is_stored_as_text(c):
    r = c.post("/api/comments", json={"auteur": "Test", "message": "<script>alert(1)</script> coucou"})
    assert r.status_code == 201 and "<script>" in r.json()["message"]     # stocké tel quel ; React l'échappe à l'affichage


def test_rate_limit(c, monkeypatch):
    monkeypatch.setenv("COMMENTS_PER_HOUR", "1")
    assert c.post("/api/comments", json={"auteur": "Spam", "message": "Encore un message"}).status_code == 429


def test_moderation_mode(c, monkeypatch):
    monkeypatch.setenv("COMMENTS_AUTO_APPROVE", "false")
    r = c.post("/api/comments", json={"auteur": "Nadia", "message": "En attente de validation"})
    cid = r.json()["id"]
    assert r.status_code == 201 and r.json()["approved"] is False
    assert all(x["id"] != cid for x in c.get("/api/comments").json())                       # invisible au public
    assert any(x["id"] == cid for x in c.get("/api/admin/comments", headers=ADM).json())
    assert c.post(f"/api/admin/comments/{cid}/approve", headers=ADM).json()["approved"] is True
    assert any(x["id"] == cid for x in c.get("/api/comments").json())
    assert c.delete(f"/api/admin/comments/{cid}", headers=ADM).status_code == 204
    assert all(x["id"] != cid for x in c.get("/api/comments").json())
