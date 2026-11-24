"""Traduit le formulaire du front (Match.jsx) vers le profil attendu par le modèle PetMatch.
C'est LE point à ajuster si vous changez le formulaire ou la logique métier."""
from .schemas import ProfilIn

# Seuils de surface (m²) -> type d'appartement. HYPOTHÈSE MÉTIER : à valider/modifier ici uniquement.
SURFACE_F2_MAX = 45     # < 45 m²  -> F2
SURFACE_F3_MAX = 75     # < 75 m²  -> F3, sinon F4


def logement_modele(p: ProfilIn) -> str:
    """Type de logement du modèle (F2 < F3 < F4 < Maison < Villa) à partir de logement + surface + jardin.
    Seuils de surface = HYPOTHÈSE à valider."""
    if p.logement == "maison":
        return "Villa avec jardin/cour" if p.jardin == "oui" else "Maison traditionnelle"
    if p.surface < SURFACE_F2_MAX:
        return "Appartement F2"
    if p.surface < SURFACE_F3_MAX:
        return "Appartement F3"
    return "Appartement F4"


def to_model_profile(p: ProfilIn) -> dict:
    return {
        "Type_Logement": logement_modele(p),
        "Budget_Mensuel_DZD": p.budget,
        # Le champ du formulaire est maintenant « Heures à la maison par jour » = présence directe
        # (le modèle calcule l'absence = 16 h - présence).
        "Heures_Presence_Jour": p.temps,
        "Nombre_Enfants": 1 if p.enfants == "oui" else 0,
        "Experience_Animaux": "Débutant" if p.experience == "aucune" else "Intermédiaire",
    }
