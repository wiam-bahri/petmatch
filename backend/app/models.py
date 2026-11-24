"""Tables SQLAlchemy."""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Animal(Base):
    """Animal du refuge. Les 6 premières colonnes de données = ce que lit le front ;
    les colonnes ML (race, cost_dzd...) = ce que lit le modèle PetMatch."""
    __tablename__ = "animals"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(60))
    espece: Mapped[str] = mapped_column(String(20))      # chat | chien | lapin  (front)
    age: Mapped[float] = mapped_column(Float)
    taille: Mapped[str] = mapped_column(String(10))      # petite | moyenne | grande
    energie: Mapped[int] = mapped_column(Integer)        # 1..5
    wilaya: Mapped[str] = mapped_column(String(40))
    asso: Mapped[str] = mapped_column(String(60))
    img: Mapped[str] = mapped_column(String(200))
    # --- colonnes pour le modèle ML
    race: Mapped[str] = mapped_column(String(60))        # doit exister dans le catalogue d'entraînement
    cost_dzd: Mapped[float] = mapped_column(Float)       # coût mensuel estimé
    chronic: Mapped[bool] = mapped_column(Boolean, default=False)
    behavior: Mapped[bool] = mapped_column(Boolean, default=False)


class Adopter(Base):
    """Profil envoyé par le formulaire + résultat du matching (pour relire chaque adoptant)."""
    __tablename__ = "adopters"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    profil: Mapped[dict] = mapped_column(JSON)           # profil brut du front
    profil_modele: Mapped[dict] = mapped_column(JSON)    # profil traduit pour le modèle
    resultats: Mapped[list] = mapped_column(JSON)


class Comment(Base):
    """Commentaire laissé par un visiteur : sur un animal (animal_id) ou général (animal_id = NULL).
    Aucun commentaire n'est pré-rempli : tout vient des visiteurs."""
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int | None] = mapped_column(ForeignKey("animals.id"), nullable=True, index=True)
    auteur: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    note: Mapped[int | None] = mapped_column(Integer, nullable=True)         # 1..5, facultatif
    approved: Mapped[bool] = mapped_column(Boolean, default=True)
    ip_hash: Mapped[str] = mapped_column(String(16), index=True)             # hash tronqué (anti-spam), pas l'IP
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
