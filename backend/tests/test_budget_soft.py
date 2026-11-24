"""Regression tests: blocked pets should retain an informative score, not forced 0%."""
import pathlib
import sys
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "petmatch"))
from matcher import Matcher, load_animals
from petmatch_algorithm import PetMatchModel


def test_budget_block_keeps_nonzero_informative_score():
    model = PetMatchModel.load(str(BASE / "models" / "petmatch_algorithm.pkl"))
    assert "budget" in model.cfg.hard_rules  # affordability remains a safety decision
    animals = load_animals(str(BASE / "data" / "petmatch_animals_clean.csv"))
    model.m = Matcher(animals, model.cfg)
    profile = {
        "Type_Logement": "Appartement F3",
        "Budget_Mensuel_DZD": 10000,
        "Heures_Presence_Jour": 8,
        "Nombre_Enfants": 0,
        "Experience_Animaux": "Débutant",
        "Espece": "Cat",
        "Race": None,
        "Taille_Foyer": 1,
    }
    a, warnings, idx, D, proba, score, compatible = model._score_all(profile)
    budget_blocked = D["block_budget"].to_numpy()
    assert budget_blocked.any()
    assert not compatible[budget_blocked].any()
    assert np.any(score[budget_blocked] > 0)
    assert np.any(score > 0)
