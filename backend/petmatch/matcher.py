"""Moteur de matching multicritère PetMatch Algeria.

Pipeline : règles éliminatoires -> score de compatibilité [0,1] -> Top-K + explications.
Les motifs de refus et les points forts sont GÉNÉRÉS à partir des mêmes colonnes
(paramètres + masques) que celles qui ont servi au filtrage : pas de texte écrit à la main
par cas, donc cohérence garantie entre filtrage et explication.
La colonne Cible_Compatible n'est JAMAIS utilisée ici (évaluation uniquement, cf. evaluate.py).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from config import (Config, HOUSING_LEVEL, HOUSING_LABEL, EXPERIENCE_LEVEL, EXPERIENCE_LABEL)

RULES = ("budget", "logement", "solitude", "enfants", "experience")
ADOPTER_FIELDS = ["Type_Logement", "Budget_Mensuel_DZD", "Heures_Presence_Jour",
                  "Nombre_Enfants", "Experience_Animaux"]


def fmt_dzd(x):
    return f"{int(round(float(x))):,}".replace(",", " ")


def fmt_h(x):
    return f"{float(x):g}"


# ----------------------------------------------------------------------------- données
def load_animals(path_or_df) -> pd.DataFrame:
    df = pd.read_csv(path_or_df) if isinstance(path_or_df, str) else path_or_df.copy()
    out = pd.DataFrame({
        "pet_id": df["pet_id"], "pet_name": df["pet_name"], "Espece": df["Espece"],
        "Race": df["Race"], "size_class": df["size_class"], "age_years": df["age_years"],
        "cost_dzd": df["estimated_monthly_cost_dzd"].astype(float),
        "exercise_min": df["daily_exercise_minutes"].astype(float),
        "chronic": df["chronic_condition"].fillna(0).astype(int),
        "behavior": df["behavior_issues"].fillna(0).astype(int),
    })
    return out.dropna(subset=["Espece", "Race", "cost_dzd"]).reset_index(drop=True)


def clean_adopter(raw: dict):
    """Normalise un profil ; champs absents/invalides -> NaN + avertissement (cas limite 'profil incomplet')."""
    warnings, a = [], {}
    labels = {"Type_Logement": "type de logement", "Budget_Mensuel_DZD": "budget mensuel",
              "Heures_Presence_Jour": "heures de présence", "Nombre_Enfants": "nombre d'enfants",
              "Experience_Animaux": "expérience avec les animaux"}
    lvl = HOUSING_LEVEL.get(raw.get("Type_Logement"))
    exp = EXPERIENCE_LEVEL.get(raw.get("Experience_Animaux"))
    a["housing"], a["exp"] = (np.nan if lvl is None else lvl), (np.nan if exp is None else exp)
    for key, name, lo, hi in [("Budget_Mensuel_DZD", "budget", 0, None), ("Heures_Presence_Jour", "presence", 0, 24),
                              ("Nombre_Enfants", "kids", 0, None)]:
        v = raw.get(key)
        try:
            v = float(v)
            if np.isnan(v) or v < lo or (hi is not None and v > hi):
                raise ValueError
        except (TypeError, ValueError):
            v = np.nan
        a[name] = v
    for k in ["housing", "exp", "budget", "presence", "kids"]:
        if np.isnan(a[k]):
            src = {"housing": "Type_Logement", "exp": "Experience_Animaux", "budget": "Budget_Mensuel_DZD",
                   "presence": "Heures_Presence_Jour", "kids": "Nombre_Enfants"}[k]
            warnings.append(f"Information manquante ou invalide : {labels[src]}. Ce critère n'a pas été évalué ; le résultat est moins fiable.")
    a["pref_esp"], a["pref_race"] = raw.get("Espece"), raw.get("Race")
    return a, warnings


# ----------------------------------------------------------------------------- moteur
class Matcher:
    def __init__(self, animals: pd.DataFrame, cfg: Config | None = None):
        self.cfg = cfg or Config()
        self.animals = animals.reset_index(drop=True)
        self.A = self._prepare(self.animals)
        self._id2idx = {pid: i for i, pid in enumerate(self.animals["pet_id"])}

    # --- paramètres côté animal (ne dépendent pas de l'adoptant -> calculés une fois)
    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg, kb = self.cfg, self.cfg.kb
        A = df.reset_index(drop=True).copy()

        def param(key, default):
            v = pd.to_numeric(A["Espece"].map({s: d.get(key) for s, d in kb["species"].items()}), errors="coerce")
            if cfg.use_race_overrides:
                for race, d in kb["races"].items():
                    if key in d:
                        v = v.mask(A["Race"] == race, d[key])
            return v.fillna(default).to_numpy(float)

        A["p_min_housing"] = param("min_housing", 1)
        for sp, d in kb["size_min_housing"].items():
            for size, lvl in d.items():
                m = ((A["Espece"] == sp) & (A["size_class"] == size)).to_numpy()
                A.loc[m, "p_min_housing"] = np.maximum(A.loc[m, "p_min_housing"], lvl)
        A["p_max_sol"] = param("max_solitude_h", np.inf) * cfg.solitude_scale
        A["p_max_kids"] = param("max_children", np.inf)
        A["p_child_sens"] = param("child_sensitivity", 0.05)
        A["p_need_exp"] = param("need_experience", 0)
        A["p_eff_cost"] = A["cost_dzd"] * (1 + cfg.chronic_cost_uplift * A["chronic"])
        A["p_req_exp"] = np.maximum(A["behavior"] * 1.0, A["p_need_exp"] if cfg.race_experience_hard else 0)
        return A

    # --- calcul vectorisé (adoptant scalaire OU tableau aligné ligne à ligne avec A)
    def _compute(self, A: pd.DataFrame, ad: dict) -> pd.DataFrame:
        cfg = self.cfg
        n = len(A)
        g = lambda k: np.broadcast_to(np.asarray(ad[k], dtype=float), (n,))
        housing, exp, budget, presence, kids = g("housing"), g("exp"), g("budget"), g("presence"), g("kids")
        absence = np.maximum(0.0, cfg.waking_hours - presence)
        D = pd.DataFrame(index=A.index)
        D["absence_h"] = absence
        with np.errstate(invalid="ignore", divide="ignore"):
            # ---- règles éliminatoires (une comparaison avec NaN vaut False : critère non évalué)
            blocks = {
                "budget": budget < A["p_eff_cost"].to_numpy() * cfg.budget_tol,
                "logement": housing < A["p_min_housing"].to_numpy(),
                "solitude": absence > A["p_max_sol"].to_numpy(),
                "enfants": kids > A["p_max_kids"].to_numpy(),
                "experience": exp < A["p_req_exp"].to_numpy(),
            }
            for r in RULES:
                D[f"block_{r}"] = blocks[r] if r in cfg.hard_rules else np.zeros(n, bool)
            D["blocked"] = D[[f"block_{r}" for r in RULES]].any(axis=1)

            # ---- sous-scores continus dans [0,1] (NaN si donnée adoptant manquante)
            ratio = budget / A["p_eff_cost"].to_numpy()
            S = {
                "budget": np.clip(ratio / cfg.budget_tol, 0, 2) / 2,
                "logement": np.clip(0.6 + 0.2 * (housing - A["p_min_housing"].to_numpy()), 0, 1),
                "presence": np.clip(1 - absence / A["p_max_sol"].to_numpy(), 0, 1),
                "enfants": np.clip(1 - A["p_child_sens"].to_numpy() * kids, 0, 1),
                "experience": 1 - 0.5 * np.maximum(A["p_need_exp"].to_numpy() - exp, 0),
                "activite": np.where(A["exercise_min"].to_numpy() <= 0, 1.0,
                                     np.clip(presence * 10 / np.maximum(A["exercise_min"].to_numpy(), 1e-9), 0, 1)),
                "sante": 1 - (0.4 * A["chronic"].to_numpy() + 0.3 * A["behavior"].to_numpy())
                         * (1 - 0.25 * np.nan_to_num(exp, nan=0.0)),
            }
            pe, pr = ad.get("pref_esp"), ad.get("pref_race")
            if cfg.use_preference and pe is not None and not (isinstance(pe, float) and np.isnan(pe)):
                S["preference"] = np.where(A["Race"].to_numpy() == pr, 1.0,
                                           np.where(A["Espece"].to_numpy() == pe, 0.6, 0.0))
            else:
                S["preference"] = np.full(n, np.nan)
        W = np.array([cfg.weights[k] for k in S])
        M = np.column_stack([S[k] for k in S])
        avail = ~np.isnan(M)
        wsum = (avail * W).sum(axis=1)
        raw = np.where(wsum > 0, np.nansum(np.where(avail, M, 0) * W, axis=1) / np.where(wsum > 0, wsum, 1), np.nan)
        for k in S:
            D[f"s_{k}"] = S[k]
        enabled_w = sum(cfg.weights[k] for k in S if k != "preference" or cfg.use_preference)
        D["confidence"] = wsum / enabled_w
        D["score_raw"] = np.clip(raw, 0, 1)
        D["compatible"] = (~D["blocked"]) & (D["score_raw"] >= cfg.seuil_score)
        # Score descriptif indépendant du verdict : un blocage (ex. budget) ne masque plus le degré de compatibilité.
        D["score"] = D["score_raw"]
        return D

    def _adopter_D(self, adopter: dict, A: pd.DataFrame | None = None):
        a, warns = clean_adopter(adopter)
        A = self.A if A is None else A
        return a, warns, self._compute(A, a)

    # --- explications générées depuis les règles réellement déclenchées
    def block_reasons(self, a: dict, A_row: pd.Series, D_row: pd.Series) -> list[str]:
        out = []
        if D_row["block_budget"]:
            need = A_row["p_eff_cost"] * self.cfg.budget_tol
            extra = " (suivi vétérinaire d'une maladie chronique inclus)" if A_row["chronic"] else ""
            out.append(f"Le budget nécessaire pour cet animal est d'environ {fmt_dzd(need)} DZD par mois{extra}, "
                       f"alors que votre budget est de {fmt_dzd(a['budget'])} DZD.")
        if D_row["block_logement"]:
            out.append(f"Cet animal nécessite au minimum un logement de type « {HOUSING_LABEL[int(A_row['p_min_housing'])]} », "
                       f"vous vivez en « {HOUSING_LABEL[int(a['housing'])]} ».")
        if D_row["block_solitude"]:
            out.append(f"Cet animal supporte au maximum {fmt_h(A_row['p_max_sol'])} h de solitude par jour, "
                       f"vous êtes absent environ {fmt_h(D_row['absence_h'])} h.")
        if D_row["block_enfants"]:
            out.append(f"Cet animal ne convient pas à un foyer de plus de {int(A_row['p_max_kids'])} enfant(s), "
                       f"vous en avez {int(a['kids'])}.")
        if D_row["block_experience"]:
            why = "des troubles du comportement sont signalés" if A_row["behavior"] else "sa race est exigeante"
            out.append(f"Cet animal demande une expérience au moins « {EXPERIENCE_LABEL[int(A_row['p_req_exp'])]} » ({why}), "
                       f"votre niveau est « {EXPERIENCE_LABEL[int(a['exp'])]} ».")
        return out

    def rules_passed(self, a: dict, A_row: pd.Series, D_row: pd.Series) -> list[str]:
        """Règles de sécurité RESPECTÉES (phrases générées avec les valeurs réellement comparées)."""
        out, hard = [], self.cfg.hard_rules
        if "budget" in hard and not np.isnan(a["budget"]) and not D_row["block_budget"]:
            marge = (self.cfg.budget_tol - 1) * 100
            extra = f" (coût estimé ~{fmt_dzd(A_row['p_eff_cost'])} DZD + marge de sécurité de {marge:.0f} %)" if marge > 0.5 else ""
            out.append(f"Budget : le budget nécessaire pour cet animal est d'environ {fmt_dzd(A_row['p_eff_cost'] * self.cfg.budget_tol)} DZD/mois{extra} ; "
                       f"votre budget de {fmt_dzd(a['budget'])} DZD le couvre.")
        if "logement" in hard and not np.isnan(a["housing"]) and not D_row["block_logement"]:
            out.append(f"Logement : votre logement « {HOUSING_LABEL[int(a['housing'])]} » répond au minimum requis "
                       f"(« {HOUSING_LABEL[int(A_row['p_min_housing'])]} »).")
        if "solitude" in hard and not np.isnan(a["presence"]) and not D_row["block_solitude"]:
            if np.isfinite(A_row["p_max_sol"]):
                out.append(f"Présence : vous êtes absent environ {fmt_h(D_row['absence_h'])} h/jour, "
                           f"cet animal en supporte jusqu'à {fmt_h(A_row['p_max_sol'])} h.")
            else:
                out.append("Présence : cet animal n'a pas de limite stricte de solitude.")
        if "enfants" in hard and not np.isnan(a["kids"]) and not D_row["block_enfants"]:
            if np.isfinite(A_row["p_max_kids"]):
                out.append(f"Enfants : cet animal convient à un foyer de {int(A_row['p_max_kids'])} enfant(s) maximum, vous en avez {int(a['kids'])}.")
            else:
                out.append("Enfants : aucune limite stricte pour cet animal dans votre situation.")
        if "experience" in hard and not np.isnan(a["exp"]) and not D_row["block_experience"]:
            if A_row["p_req_exp"] > 0:
                out.append(f"Expérience : niveau requis « {EXPERIENCE_LABEL[int(A_row['p_req_exp'])]} », votre niveau « {EXPERIENCE_LABEL[int(a['exp'])]} ».")
            else:
                out.append("Expérience : aucun niveau minimal n'est exigé pour cet animal.")
        for key, label in [("budget", "budget"), ("housing", "type de logement"), ("presence", "heures de présence"),
                           ("kids", "nombre d'enfants"), ("exp", "expérience")]:
            if np.isnan(a[key]):
                out.append(f"Non évalué : {label} non renseigné.")
        return out

    def unblock_conditions(self, a: dict, A_row: pd.Series, D_row: pd.Series) -> list[str]:
        """Ce qui devrait changer pour que la règle déclenchée ne bloque plus (même source que block_reasons)."""
        out = []
        if D_row["block_budget"]:
            out.append(f"Disposer d'un budget d'au moins {fmt_dzd(A_row['p_eff_cost'] * self.cfg.budget_tol)} DZD par mois.")
        if D_row["block_logement"]:
            out.append(f"Disposer d'un logement de type « {HOUSING_LABEL[int(A_row['p_min_housing'])]} » ou supérieur.")
        if D_row["block_solitude"]:
            out.append(f"Être présent au moins {fmt_h(max(0.0, self.cfg.waking_hours - A_row['p_max_sol']))} h par jour.")
        if D_row["block_enfants"]:
            out.append(f"Choisir un animal adapté aux familles de plus de {int(A_row['p_max_kids'])} enfant(s).")
        if D_row["block_experience"]:
            out.append(f"Acquérir le niveau « {EXPERIENCE_LABEL[int(A_row['p_req_exp'])]} » ou être accompagné par un professionnel.")
        return out

    def strengths_and_watchouts(self, a, A_row, D_row):
        st, wo = [], []
        s = lambda k: D_row[f"s_{k}"]
        ok = lambda k, th=0.8: (not np.isnan(s(k))) and s(k) >= th
        low = lambda k, th=0.5: (not np.isnan(s(k))) and s(k) < th
        if ok("budget", 0.75): st.append(f"Son coût (~{fmt_dzd(A_row['p_eff_cost'])} DZD/mois) reste confortable par rapport à votre budget.")
        if low("budget", 0.55): wo.append(f"Son coût (~{fmt_dzd(A_row['p_eff_cost'])} DZD/mois) laisse peu de marge sur votre budget.")
        if ok("logement"): st.append(f"Votre logement ({HOUSING_LABEL[int(a['housing'])]}) est bien adapté à ses besoins d'espace.")
        if low("logement", 0.7): wo.append("Votre logement est juste suffisant pour cet animal.")
        if ok("presence") and A_row["p_max_sol"] < 24: st.append("Il supporte bien vos heures d'absence.")
        if low("presence"): wo.append(f"Vos absences (~{fmt_h(D_row['absence_h'])} h/jour) sont proches de sa limite de tolérance.")
        if ok("enfants", 0.85) and a["kids"] > 0: st.append(f"Il s'accorde bien avec un foyer de {int(a['kids'])} enfant(s).")
        if low("enfants", 0.6): wo.append("Une surveillance est nécessaire avec de jeunes enfants.")
        if ok("experience") and A_row["p_need_exp"] > 0: st.append("Votre expérience correspond à ses besoins.")
        if low("experience", 0.8): wo.append("Il demande plus d'expérience que la vôtre : prévoyez un accompagnement.")
        if ok("activite") and A_row["exercise_min"] >= 30: st.append("Votre présence permet de couvrir ses besoins d'activité.")
        if low("activite"): wo.append("Il a besoin de plus d'activité que votre temps de présence n'en permet.")
        if A_row["chronic"] or A_row["behavior"]:
            items = (["maladie chronique"] if A_row["chronic"] else []) + (["troubles du comportement"] if A_row["behavior"] else [])
            wo.append("Santé/comportement à surveiller : " + " et ".join(items) + ".")
        elif ok("sante", 0.99): st.append("Aucun problème de santé ou de comportement signalé.")
        if not np.isnan(s("preference")):
            if s("preference") == 1: st.append("Correspond à la race que vous souhaitiez.")
            elif s("preference") > 0: st.append("Correspond à l'espèce que vous souhaitiez.")
        return st, wo

    # --- API publique
    def evaluate_pair(self, adopter: dict, pet_id: str) -> dict:
        """Verdict détaillé pour UN animal : tous les motifs bloquants sont listés (pas seulement le premier)."""
        a, warns, D = self._adopter_D(adopter)
        i = self._id2idx[pet_id]
        A_row, D_row = self.A.iloc[i], D.iloc[i]
        reasons = self.block_reasons(a, A_row, D_row)
        st, wo = self.strengths_and_watchouts(a, A_row, D_row)
        verdict = bool(D_row["compatible"])
        if not reasons and not verdict:
            reasons = [f"Le score de compatibilité ({D_row['score_raw']:.2f}) est inférieur au seuil minimal ({self.cfg.seuil_score:.2f})."]
        return {"pet_id": pet_id, "pet_name": A_row["pet_name"], "Espece": A_row["Espece"], "Race": A_row["Race"],
                "compatible": verdict, "score": float(D_row["score"]), "motifs_bloquants": reasons,
                "points_forts": st if verdict else [], "points_vigilance": wo if not D_row["blocked"] else [], "avertissements_profil": warns,
                "confiance_profil": float(D_row["confidence"])}

    def recommend(self, adopter: dict, consulted_id: str | None = None, k: int = 5, scope: str = "all",
                  max_per_race: int = 2) -> dict:
        """Top-k des animaux compatibles (même algorithme que le filtrage), animal consulté exclu."""
        a, warns, D = self._adopter_D(adopter)
        out = {"avertissements_profil": warns, "consulte": None}
        if consulted_id is not None:
            out["consulte"] = self.evaluate_pair(adopter, consulted_id)
        pool = D["compatible"].to_numpy().copy()
        if scope == "species" and a["pref_esp"] is not None:
            pool &= (self.A["Espece"] == a["pref_esp"]).to_numpy()
        if consulted_id is not None:
            pool[self._id2idx[consulted_id]] = False
        cand = (D[pool].assign(pet_id=self.A.loc[pool, "pet_id"], margin=a["budget"] / self.A.loc[pool, "p_eff_cost"]
                               if not np.isnan(a["budget"]) else 0.0)
                .sort_values(["score", "margin", "pet_id"], ascending=[False, False, True]))  # ex-aequo départagés par marge budgétaire
        # diversité : au plus `max_per_race` animaux par race (pour pouvoir comparer des options), complété si besoin
        races, picked, skipped = {}, [], []
        for idx in cand.index:
            rc = self.A.at[idx, "Race"]
            (picked if races.get(rc, 0) < max_per_race else skipped).append(idx)
            races[rc] = races.get(rc, 0) + (1 if len(picked) and picked[-1] == idx else 0)
            if len(picked) >= k: break
        picked = (picked + skipped)[:k]
        cand = cand.loc[picked]
        recs = []
        for idx in cand.index:
            st, wo = self.strengths_and_watchouts(a, self.A.loc[idx], D.loc[idx])
            r = self.A.loc[idx]
            recs.append({"rang": len(recs) + 1, "pet_id": r["pet_id"], "pet_name": r["pet_name"], "Espece": r["Espece"],
                         "Race": r["Race"], "age_years": float(r["age_years"]), "score": round(float(D.loc[idx, "score"]), 4),
                         "points_forts": st[:3], "points_vigilance": wo})
        out["top"] = recs
        n_comp = int(pool.sum())
        if n_comp == 0:
            out["message"] = "Aucun animal compatible avec votre profil n'a été trouvé. " + self._blocking_summary(D)
        elif n_comp < k:
            out["message"] = f"Seulement {n_comp} animal(aux) compatible(s) disponible(s) ; voici tous ceux qui conviennent."
        else:
            out["message"] = "Voici les 5 animaux les plus adaptés à votre profil." if k == 5 else f"Top {k} des animaux les plus adaptés."
        if warns and n_comp > 0:
            out["message"] += " Attention : votre profil est incomplet, complétez-le pour des recommandations plus fiables."
        out["n_compatibles"] = n_comp
        return out

    def _blocking_summary(self, D: pd.DataFrame) -> str:
        names = {"budget": "budget", "logement": "type de logement", "solitude": "heures d'absence",
                 "enfants": "nombre d'enfants", "experience": "niveau d'expérience"}
        cnt = {names[r]: int(D[f"block_{r}"].sum()) for r in RULES}
        cnt = {k: v for k, v in sorted(cnt.items(), key=lambda x: -x[1]) if v > 0}
        if not cnt:
            return "Aucun animal n'atteint le score minimal requis."
        top = ", ".join(f"{k} ({v} animaux exclus)" for k, v in list(cnt.items())[:3])
        return f"Principaux critères bloquants : {top}."

    # --- évaluation au niveau "race souhaitée" (pour comparer à Cible_Compatible)
    def race_profiles(self) -> pd.DataFrame:
        df = self.animals
        g = df.groupby("Race")
        prof = pd.DataFrame({
            "Espece": g["Espece"].agg(lambda s: s.mode().iloc[0]),
            "size_class": g["size_class"].agg(lambda s: s.mode().iloc[0]),
            "age_years": g["age_years"].median(),
            "cost_dzd": g["cost_dzd"].quantile(self.cfg.cost_quantile),
            "exercise_min": g["exercise_min"].median(),
        })
        prof["chronic"], prof["behavior"] = 0, 0
        prof = prof.reset_index()
        prof["pet_id"] = "RACE::" + prof["Race"]
        prof["pet_name"] = prof["Race"]
        return prof

    def _ad_arrays(self, adopters: pd.DataFrame) -> dict:
        return {"housing": adopters["Type_Logement"].map(HOUSING_LEVEL).to_numpy(float),
                "exp": adopters["Experience_Animaux"].map(EXPERIENCE_LEVEL).to_numpy(float),
                "budget": adopters["Budget_Mensuel_DZD"].to_numpy(float),
                "presence": adopters["Heures_Presence_Jour"].to_numpy(float),
                "kids": adopters["Nombre_Enfants"].to_numpy(float),
                "pref_esp": None, "pref_race": None}

    def predict_desired_race(self, adopters: pd.DataFrame) -> pd.DataFrame:
        """Verdict de l'algorithme pour (adoptant, race souhaitée) -> comparé à Cible_Compatible."""
        saved = self.cfg.use_preference
        self.cfg.use_preference = False
        try:
            P = self._prepare(self.race_profiles()).set_index("Race", drop=False)
            A = P.loc[adopters["Race"]].reset_index(drop=True)
            D = self._compute(A, self._ad_arrays(adopters))
        finally:
            self.cfg.use_preference = saved
        D.index = adopters.index
        return D

    def race_score_matrix(self, adopters: pd.DataFrame):
        """Score_raw (n_adoptants x n_races), -1 pour les races bloquées ; sans bonus de préférence."""
        saved = self.cfg.use_preference
        self.cfg.use_preference = False
        try:
            P = self._prepare(self.race_profiles())
            ad = self._ad_arrays(adopters)
            races = list(P["Race"])
            M = np.zeros((len(adopters), len(races)))
            for j in range(len(races)):
                A = pd.concat([P.iloc[[j]]] * len(adopters), ignore_index=True)
                D = self._compute(A, ad)
                M[:, j] = np.where(D["blocked"], -1.0, D["score_raw"])
        finally:
            self.cfg.use_preference = saved
        return M, races
