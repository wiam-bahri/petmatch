"""Pydantic : validation des entrées / forme des sorties (contrat avec le front)."""
from datetime import datetime
from typing import Literal, Optional
from datetime import timezone
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfilIn(BaseModel):
    """Exactement les champs du formulaire Match.jsx."""
    logement: Literal["appartement", "maison"] = "appartement"
    surface: float = Field(ge=10, le=2000)
    jardin: Literal["oui", "non"] = "non"
    enfants: Literal["oui", "non"] = "non"
    experience: Literal["aucune", "oui"] = "aucune"
    temps: float = Field(ge=0, le=24)          # "Temps libre par jour (h)"
    budget: float = Field(ge=0)                # DZD / mois
    wilaya: str = "Alger"


ESPECES = Literal["chat", "chien", "lapin", "oiseau", "poisson", "reptile", "mammifere"]


class AnimalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str
    espece: str
    race: str = ""
    nb_commentaires: int = 0
    age: float
    taille: str
    energie: int
    wilaya: str
    asso: str
    img: str


class MatchItem(BaseModel):
    """[{id, nom, espece, img, score, raisons[]}] attendu par le front (+ champs bonus)."""
    id: int
    nom: str
    espece: str
    img: str
    score: int                  # 0..100
    raisons: list[str]          # codes : good, budget, bigSmall, energyTime, firstDog, kids
    compatible: bool
    details: list[str] = []     # phrases lisibles (FR) générées par le modèle


class AdopterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    profil: dict
    resultats: list


class AnimalIn(BaseModel):
    """Ajout d'un animal : champs du front + 'race' (doit exister dans le catalogue du modèle)."""
    nom: str = Field(min_length=1, max_length=60)
    espece: ESPECES
    age: float = Field(ge=0, le=30)
    taille: Literal["petite", "moyenne", "grande"]
    energie: int = Field(ge=1, le=5)
    wilaya: str = Field(min_length=1, max_length=40)
    asso: str = Field(min_length=1, max_length=60)
    img: str = Field(pattern=r"^/(animals|pets)/[\w\-/]+\.(png|webp|jpg)$")   # fichier dans frontend/public/
    race: str
    cost_dzd: Optional[float] = Field(default=None, gt=0)        # vide -> coût médian de la race
    chronic: bool = False
    behavior: bool = False


URL_RE = re.compile(r"(https?://|www\.|\b[\w-]+\.(com|net|org|ru|xyz|top|info)\b)", re.I)


class CommentIn(BaseModel):
    animal_id: Optional[int] = None                       # None = commentaire général sur le site
    auteur: str = Field(min_length=2, max_length=40)
    message: str = Field(min_length=5, max_length=600)
    note: Optional[int] = Field(default=None, ge=1, le=5)
    site: str = ""                                        # champ piège anti-robot (doit rester vide)

    @field_validator("auteur", "message")
    @classmethod
    def clean(cls, v: str) -> str:
        v = re.sub(r"\s+", " ", v).strip()
        if URL_RE.search(v):
            raise ValueError("Les liens ne sont pas autorisés dans les commentaires.")
        return v


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    animal_id: Optional[int] = None
    auteur: str
    message: str
    note: Optional[int] = None
    approved: bool = True
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def utc(cls, v: datetime) -> datetime:
        return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v
