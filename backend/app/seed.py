"""Remplit la base avec le catalogue si elle est vide (SQLite sur Render gratuit est éphémère -> re-seed automatique)."""
import os
import pandas as pd
from sqlalchemy.orm import Session
from .models import Animal
from .db import BASE
from .catalog import CATALOG


def seed_if_empty(db: Session):
    if db.query(Animal).count():
        return
    cat = pd.read_csv(os.path.join(BASE, "data", "petmatch_animals_clean.csv"))
    cost = cat.groupby("Race")["estimated_monthly_cost_dzd"].median()   # coût mensuel médian par race
    for nom, esp, race, age, taille, ener, wil, asso, img, chronic, behavior in CATALOG:
        db.add(Animal(nom=nom, espece=esp, race=race, age=age, taille=taille, energie=ener, wilaya=wil, asso=asso,
                      img=img, cost_dzd=float(cost[race]), chronic=chronic, behavior=behavior))
    db.commit()
