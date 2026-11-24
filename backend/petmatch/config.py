"""Configuration et base de connaissances du moteur de matching PetMatch Algeria.

Tout ce qui est "règle métier" ou "hyperparamètre" vit ici (jamais en dur dans le code),
afin que chaque version testée soit tracée (cf. experiments/matching_runs.jsonl).
"""
from dataclasses import dataclass, field, asdict
import copy

HOUSING_LEVEL = {
    "Appartement F2": 1, "Appartement F3": 2, "Appartement F4": 3,
    "Maison traditionnelle": 4, "Villa avec jardin/cour": 5,
}
HOUSING_LABEL = {v: k for k, v in HOUSING_LEVEL.items()}
EXPERIENCE_LEVEL = {"Débutant": 0, "Intermédiaire": 1, "Expert": 2}
EXPERIENCE_LABEL = {v: k for k, v in EXPERIENCE_LEVEL.items()}

# --- Base de connaissances (HYPOTHÈSES MÉTIER à valider avec vétérinaires / refuges) ---
# None = pas de limite.  max_solitude_h : heures d'absence tolérées par jour.
KNOWLEDGE = {
    "species": {
        "Dog":          dict(min_housing=2, max_solitude_h=8,  max_children=None, child_sensitivity=0.06, need_experience=0),
        "Cat":          dict(min_housing=1, max_solitude_h=12, max_children=None, child_sensitivity=0.05, need_experience=0),
        "Bird":         dict(min_housing=1, max_solitude_h=10, max_children=None, child_sensitivity=0.06, need_experience=0),
        "Fish":         dict(min_housing=1, max_solitude_h=24, max_children=2,    child_sensitivity=0.10, need_experience=0),
        "Rabbit":       dict(min_housing=1, max_solitude_h=10, max_children=None, child_sensitivity=0.08, need_experience=0),
        "Reptile":      dict(min_housing=1, max_solitude_h=24, max_children=None, child_sensitivity=0.05, need_experience=0),
        "Small Mammal": dict(min_housing=1, max_solitude_h=14, max_children=None, child_sensitivity=0.10, need_experience=0),
    },
    # Surcharges par race (optionnelles, activables via cfg.use_race_overrides)
    "races": {
        "Siberian Husky":      dict(max_solitude_h=6, need_experience=1, min_housing=3),
        "Labrador Retriever":  dict(max_solitude_h=6, min_housing=3),
        "Macaw":               dict(max_solitude_h=5, need_experience=2, min_housing=3),
        "African Grey Parrot": dict(max_solitude_h=6, need_experience=1),
        "Ball Python":         dict(need_experience=1),
        "Ferret":              dict(need_experience=1, max_solitude_h=10),
        "Flemish Giant":       dict(min_housing=2),
        "Chinchilla":          dict(need_experience=1),
    },
    # Logement minimum supplémentaire selon la taille (espèce -> taille -> niveau)
    "size_min_housing": {"Dog": {"Large": 3, "Giant": 4}},
}

DEFAULT_WEIGHTS = {
    "budget": 0.22, "logement": 0.18, "presence": 0.18, "enfants": 0.10,
    "experience": 0.10, "activite": 0.07, "sante": 0.05, "preference": 0.10,
}


@dataclass
class Config:
    name: str = "v1_defaut"
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    seuil_score: float = 0.50          # score_raw minimal pour être "compatible"
    budget_tol: float = 1.00           # budget >= coût * tol, sinon bloquant
    chronic_cost_uplift: float = 0.25  # surcoût vétérinaire d'un animal à maladie chronique
    waking_hours: float = 16.0         # absence = max(0, waking_hours - heures de présence)
    solitude_scale: float = 1.0        # multiplicateur de tolérance à la solitude
    cost_quantile: float = 0.50        # coût "profil de race" utilisé pour l'évaluation par race
    use_race_overrides: bool = True
    hard_rules: tuple = ("budget", "logement", "solitude", "enfants", "experience")
    race_experience_hard: bool = False  # l'expérience requise par la race devient éliminatoire
    use_preference: bool = True        # bonus espèce/race souhaitées (désactivé pour l'évaluation)
    kb: dict = field(default_factory=lambda: copy.deepcopy(KNOWLEDGE))

    def to_dict(self):
        d = asdict(self)
        d.pop("kb")
        d["hard_rules"] = list(self.hard_rules)
        return d
