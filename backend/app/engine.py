"""Pont entre SQLite et le modèle PetMatch : charge model.pkl UNE fois (joblib) et note les animaux de la base."""
import os, sys, warnings
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "petmatch"))      # le .pkl référence les modules petmatch_algorithm / matcher / config
warnings.filterwarnings("ignore")
from petmatch_algorithm import PetMatchModel            # noqa: E402
from matcher import Matcher                              # noqa: E402
from .models import Animal                               # noqa: E402

SPECIES = {"chat": "Cat", "chien": "Dog", "lapin": "Rabbit", "oiseau": "Bird", "poisson": "Fish",
           "reptile": "Reptile", "mammifere": "Small Mammal"}
SIZE = {"petite": "Small", "moyenne": "Medium", "grande": "Large"}
EXERCISE_MIN = {1: 10, 2: 20, 3: 40, 4: 70, 5: 100}      # énergie 1..5 -> minutes d'exercice/jour (hypothèse)
CODE = {"budget": "budget", "logement": "bigSmall", "solitude": "energyTime", "experience": "firstDog", "enfants": "kids"}
SUB = {"budget": "budget", "logement": "bigSmall", "presence": "energyTime", "experience": "firstDog", "enfants": "kids"}


SPECIES_BACK = {v: k for k, v in SPECIES.items()}


def load_races() -> tuple[dict, dict]:
    """Races connues du modèle par espèce du front + coût mensuel médian par race (depuis le CSV d'entraînement)."""
    cat = pd.read_csv(os.path.join(BASE, "data", "petmatch_animals_clean.csv"), usecols=["Espece", "Race", "estimated_monthly_cost_dzd"])
    races = {SPECIES_BACK[sp]: sorted(g["Race"].unique().tolist()) for sp, g in cat.groupby("Espece") if sp in SPECIES_BACK}
    cost = cat.groupby("Race")["estimated_monthly_cost_dzd"].median().to_dict()
    return races, cost


class Engine:
    def __init__(self):
        self.model = None
        self.animals: list[Animal] = []
        self.races, self.cost = load_races()

    def load(self, path=None):
        self.model = PetMatchModel.load(path or os.path.join(BASE, "models", "petmatch_algorithm.pkl"))

    def set_catalog(self, db: Session):
        """Remplace le catalogue (15 000 animaux d'entraînement) par les animaux réels de la base."""
        self.animals = db.query(Animal).order_by(Animal.id).all()
        if not self.animals:        # base vide : /api/match répondra 503
            return
        df = pd.DataFrame({
            "pet_id": [str(a.id) for a in self.animals], "pet_name": [a.nom for a in self.animals],
            "Espece": [SPECIES[a.espece] for a in self.animals], "Race": [a.race for a in self.animals],
            "size_class": [SIZE[a.taille] for a in self.animals], "age_years": [a.age for a in self.animals],
            "cost_dzd": [a.cost_dzd for a in self.animals], "exercise_min": [EXERCISE_MIN[a.energie] for a in self.animals],
            "chronic": [int(a.chronic) for a in self.animals], "behavior": [int(a.behavior) for a in self.animals],
        })
        self.model.m = Matcher(df, self.model.cfg)

    def rank(self, profil: dict, k: int = 5) -> list[dict]:
        m = self.model.m
        a, _warns, _idx, D, _proba, score, ok = self.model._score_all(profil)
        raw = D["score_raw"].to_numpy()
        order = np.lexsort((-np.nan_to_num(raw), -score, -ok.astype(int)))     # compatibles d'abord, puis score
        out = []
        for i in order[:k]:
            an, A_row, D_row = self.animals[i], m.A.iloc[i], D.iloc[i]
            details = m.block_reasons(a, A_row, D_row)
            if ok[i]:
                codes = ["good"]
                details = m.strengths_and_watchouts(a, A_row, D_row)[0]
            else:
                codes = [CODE[r] for r in CODE if D_row[f"block_{r}"]]
                if not codes:   # pas bloqué mais score < seuil : on affiche le critère le plus faible
                    s = {k_: D_row[f"s_{k_}"] for k_ in SUB if f"s_{k_}" in D_row and not np.isnan(D_row[f"s_{k_}"])}
                    codes = [SUB[min(s, key=s.get)]] if s else ["good"]
                    details = [f"Score de compatibilité insuffisant ({score[i]:.0%})."]
            out.append({"id": an.id, "nom": an.nom, "espece": an.espece, "img": an.img,
                        "score": int(round(float(score[i]) * 100)), "raisons": codes,
                        "compatible": bool(ok[i]), "details": details})
        return out


engine = Engine()
