"""PetMatch Algeria - algorithme de matching ENTRAÎNÉ sur les datasets adoptants + animaux.

Pour un adoptant (et éventuellement un animal consulté), l'algorithme rend :
  1) une DÉCISION FINALE  : OUI / NON  (peut-il adopter cet animal ?)
  2) un SCORE de compatibilité entre 0 et 1
  3) si NON : TOUS les motifs bloquants, en langage simple (générés depuis les règles)
  4) le TOP 5 des animaux les plus adaptés, avec score et points forts

Architecture hybride (les deux parties sont apprises / calibrées sur les données) :
  - Sécurité  : règles éliminatoires (budget, logement, solitude, enfants, expérience) -> explicables
  - Apprentissage : modèle ML (XGBoost, hyperparamètres optimisés en validation croisée groupée par adoptant) entraîné sur des paires (adoptant, animal) avec Cible_Compatible
  - Score = alpha * proba_ML + (1 - alpha) * score_règles ; alpha et seuil appris sur prédictions hors-échantillon (out-of-fold) du jeu d'entraînement.
Cible_Compatible n'est utilisée QUE comme étiquette d'entraînement / évaluation, jamais comme entrée.

Usage :  python3 petmatch_algorithm.py (entraîne, évalue, sauvegarde, démo)
"""
from __future__ import annotations
import json, time, warnings
import numpy as np, pandas as pd, joblib
from scipy.stats import loguniform
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.model_selection import GroupKFold, RandomizedSearchCV, cross_val_predict, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from config import Config
from matcher import Matcher, load_animals, clean_adopter, RULES
warnings.filterwarnings("ignore")

SEED = 42
SIZE = {"Small": 1, "Medium": 2, "Large": 3, "Giant": 4}
#NUM = ["logement", "budget", "presence", "enfants", "foyer", "experience", "cost", "exercise", "size", "age",
       #"chronic", "behavior", "budget_ratio", "absence"]
#CAT = ["Espece", "Race"]

NUM = ["logement", "budget", "presence", "enfants", "foyer", "experience", "cost", "exercise", "size", "age",
       "chronic", "behavior", "budget_ratio", "absence", "budget_diff", "housing_diff", "exp_diff"]
CAT = ["Espece", "Race"]

class PetMatchModel:
    def __init__(self, cfg: Config | None = None, pairs_per_adopter: int = 5, seed: int = SEED):
        self.cfg, self.pairs, self.seed = cfg or Config(), pairs_per_adopter, seed
        self.alpha, self.threshold, self.pipe, self.info = 0.5, 0.5, None, {}

    # ------------------------------------------------------------------ features
    def _features(self, ad: dict, idx, foyer) -> pd.DataFrame:
        """Variables d'une paire (adoptant, animal) ; idx = positions des animaux dans le catalogue."""
        A = self.m.A.iloc[idx].reset_index(drop=True)
        n = len(A)
        g = lambda k: np.broadcast_to(np.asarray(ad[k], float), (n,))
        D = self.m._compute(A, ad)
        X = pd.DataFrame({"logement": g("housing"), "budget": g("budget"), "presence": g("presence"), "enfants": g("kids"),
                          "foyer": np.broadcast_to(np.asarray(foyer, float), (n,)), "experience": g("exp"),
                          "cost": A["p_eff_cost"], "exercise": A["exercise_min"], "size": A["size_class"].map(SIZE),
                          "age": A["age_years"], "chronic": A["chronic"], "behavior": A["behavior"],
                          "budget_ratio": g("budget") / A["p_eff_cost"], "absence": D["absence_h"],
                          "budget_diff": g("budget") - A["p_eff_cost"].to_numpy(),
                          "housing_diff": g("housing") - A["p_min_housing"].to_numpy(),
                          "exp_diff": g("exp") - A["p_req_exp"].to_numpy(),
                          "Espece": A["Espece"], "Race": A["Race"]})
        return X[NUM + CAT], D
        # X = pd.DataFrame({"logement": g("housing"), "budget": g("budget"), "presence": g("presence"), "enfants": g("kids"),
        #                   "foyer": np.broadcast_to(np.asarray(foyer, float), (n,)), "experience": g("exp"),
        #                   "cost": A["p_eff_cost"], "exercise": A["exercise_min"], "size": A["size_class"].map(SIZE),
        #                   "age": A["age_years"], "chronic": A["chronic"], "behavior": A["behavior"],
        #                   "budget_ratio": g("budget") / A["p_eff_cost"], "absence": D["absence_h"],
        #                   "Espece": A["Espece"], "Race": A["Race"]})
        # return X[NUM + CAT], D

    # ------------------------------------------------------------------ entraînement
    def fit(self, adopters: pd.DataFrame, animals: pd.DataFrame, tune: bool = True, n_iter: int = 25):
        self.m = Matcher(animals, self.cfg)
        self.foyer_default = float(adopters["Taille_Foyer"].median())
        rng = np.random.default_rng(self.seed)
        by_race = {r: np.flatnonzero((self.m.animals["Race"] == r).to_numpy()) for r in self.m.animals["Race"].unique()}
        # paires d'entraînement : chaque adoptant x quelques animaux de la race qu'il souhaite (étiquette = Cible_Compatible)
        saved, self.cfg.use_preference = self.cfg.use_preference, False
        try:
            rows, y, grp, blocked, rule = [], [], [], [], []
            for _, r in adopters.iterrows():
                cand = by_race.get(r["Race"])
                if cand is None or len(cand) == 0:
                    continue
                idx = rng.choice(cand, min(self.pairs, len(cand)), replace=False)
                a, _ = clean_adopter(r.to_dict())
                X, D = self._features(a, idx, r["Taille_Foyer"])
                rows.append(X); y += [int(r["Cible_Compatible"])] * len(X); grp += [r["ID_Adoptant"]] * len(X)
                blocked.append(D["blocked"].to_numpy()); rule.append(D["score_raw"].to_numpy())
        finally:
            self.cfg.use_preference = saved
        X, y, grp = pd.concat(rows, ignore_index=True), np.array(y), np.array(grp)
        blocked, rule = np.concatenate(blocked), np.concatenate(rule)

        pre = ColumnTransformer([("num", "passthrough", NUM),
                                 ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT)])
        base = Pipeline([("prep", pre), ("clf", XGBClassifier(eval_metric="logloss", random_state=self.seed, n_jobs=1))])
        cv = GroupKFold(5)
        if tune:   # optimisation des hyperparamètres (validation croisée groupée : un adoptant n'est jamais dans train et val)
            space = {
                     "clf__learning_rate": loguniform(0.01, 0.2),
                     "clf__max_depth": [3, 4, 5, 6],
                     "clf__n_estimators": [150, 300, 500],
                     "clf__reg_lambda": loguniform(1e-2, 10),
                     "clf__min_child_weight": [1, 3, 5],
                     "clf__subsample": [0.8, 1.0],
                     "clf__colsample_bytree": [0.8, 1.0]
                    }
            rs = RandomizedSearchCV(base, space, n_iter=n_iter, cv=cv, scoring="f1", random_state=self.seed, n_jobs=-1)
            rs.fit(X, y, groups=grp)
            base, self.info["best_params"], self.info["cv_f1"] = rs.best_estimator_, {k: (v if not isinstance(v, np.generic) else v.item()) for k, v in rs.best_params_.items()}, round(rs.best_score_, 4)
        # probabilités hors-échantillon -> apprentissage de alpha (poids ML/règles) et du seuil de décision
        oof = cross_val_predict(base, X, y, cv=cv, groups=grp, method="predict_proba")[:, 1]
        best = (-1, None)
        for alpha in np.arange(0, 1.01, 0.1):
            s = alpha * oof + (1 - alpha) * rule
            for thr in np.arange(0.30, 0.80, 0.01):
                pred = (~blocked) & (s >= thr)
                acc = accuracy_score(y, pred)
                mf1 = f1_score(y, pred, average="macro")
                score_obj = 0.5 * acc + 0.5 * mf1
                if score_obj > best[0]:
                    best = (score_obj, (float(alpha), float(thr)))
        # for alpha in np.arange(0, 1.01, 0.1):
        #     s = alpha * oof + (1 - alpha) * rule
        #     for thr in np.arange(0.30, 0.80, 0.01):
        #         pred = (~blocked) & (s >= thr)
        #         f = f1_score(y, pred, average="macro")
        #         if f > best[0]:
        #             best = (f, (float(alpha), float(thr)))
        self.alpha, self.threshold = best[1]
        self.info.update(alpha_ml=round(self.alpha, 2), seuil=round(self.threshold, 2), train_macro_f1_oof=round(best[0], 4),
                         n_pairs_train=len(X))
        self.pipe = base.fit(X, y)
        self.info["blocked_share_train_pairs"] = round(float(blocked.mean()), 3)
        return self

    # ------------------------------------------------------------------ inférence
    def _score_all(self, adopter: dict, idx=None):
        a, warns = clean_adopter(adopter)
        idx = np.arange(len(self.m.animals)) if idx is None else np.asarray(idx)
        foyer = adopter.get("Taille_Foyer", self.foyer_default)
        X, D = self._features(a, idx, foyer if foyer is not None else self.foyer_default)
        proba = self.pipe.predict_proba(X)[:, 1]
        # sans donnée adoptant (profil incomplet) : le score ML est moins fiable, on s'appuie davantage sur les règles
        score = np.clip(self.alpha * proba + (1 - self.alpha) * D["score_raw"].to_numpy(), 0, 1)
        # Afficher un score informatif même si une règle de sécurité bloque ; le verdict reste bloqué ci-dessous.
        ok = (~D["blocked"].to_numpy()) & (score >= self.threshold)
        return a, warns, idx, D, proba, score, ok

    def _texte(self, ok, score, proba, nom, race, reasons, passed, st, wo, cond, court=False):
        """Explication rédigée automatiquement (aucun texte écrit à la main par cas)."""
        L = []
        if ok:
            L.append(f"DÉCISION : OUI — vous pouvez adopter {nom} ({race}). Score de compatibilité : {score:.0%}.")
            if not court:
                L.append(f"Le modèle, entraîné sur les profils de vos données, estime la compatibilité à {proba:.0%}.")
            L.append("Pourquoi : toutes les règles de sécurité sont respectées :" if not court else "Règles respectées :")
            L += [f"  ✓ {x}" for x in passed]
            if st: L += ["Points forts :"] + [f"  + {x}" for x in st]
            if wo: L += ["À surveiller :"] + [f"  ! {x}" for x in wo]
        else:
            L.append(f"DÉCISION : NON — {nom} ({race}) n'est pas adapté à votre situation actuelle (score : {score:.0%}).")
            L.append("Motifs :")
            L += [f"  ✗ {x}" for x in reasons]
            if passed: L += ["Règles tout de même respectées :"] + [f"  ✓ {x}" for x in passed]
            if cond: L += ["Pour que ce choix devienne possible :"] + [f"  → {x}" for x in cond]
        return "\n".join(L)

    def decide(self, adopter: dict, pet_id: str) -> dict:
        """Décision finale OUI/NON pour UN animal + score + motifs."""
        i = self.m._id2idx[pet_id]
        a, warns, idx, D, proba, score, ok = self._score_all(adopter, [i])
        A_row, D_row = self.m.A.iloc[i], D.iloc[0]
        reasons = self.m.block_reasons(a, A_row, D_row)
        if not ok[0] and not reasons:
            reasons = [f"Le score de compatibilité ({score[0]:.2f}) est inférieur au seuil minimal appris ({self.threshold:.2f})."]
        st, wo = self.m.strengths_and_watchouts(a, A_row, D_row)
        passed = self.m.rules_passed(a, A_row, D_row)
        cond = self.m.unblock_conditions(a, A_row, D_row)
        wo = [] if D_row["blocked"] else wo
        texte = self._texte(bool(ok[0]), float(score[0]), float(proba[0]), A_row["pet_name"], A_row["Race"], reasons, passed,
                            st if ok[0] else [], wo, cond)
        return {"decision": "OUI" if ok[0] else "NON", "explication": texte, "regles_validees": passed,
                "conditions_pour_oui": cond, "score": round(float(score[0]), 4),
                "proba_ml": round(float(proba[0]), 4), "score_regles": round(float(D_row["score_raw"]), 4),
                "animal": {"pet_id": pet_id, "nom": A_row["pet_name"], "espece": A_row["Espece"], "race": A_row["Race"]},
                "motifs_bloquants": reasons, "points_forts": st if ok[0] else [],
                "points_vigilance": wo, "avertissements_profil": warns}

    def recommend(self, adopter: dict, consulted_id: str | None = None, k: int = 5, scope: str = "preferred",
                  max_per_race: int = 2) -> dict:
        """Top-k des animaux dont la décision est OUI, classés par score décroissant (animal consulté exclu)."""
        a, warns, idx, D, proba, score, ok = self._score_all(adopter)
        ok = ok.copy()
        if consulted_id is not None:
            ok[self.m._id2idx[consulted_id]] = False
        note = ""
        pe = adopter.get("Espece")
        if scope == "preferred" and pe:
            in_sp = (self.m.A["Espece"] == pe).to_numpy()
            if (ok & in_sp).any():
                ok &= in_sp
            else:
                note = f" Aucun animal « {pe} » compatible : recommandations élargies aux autres espèces."
        order = np.lexsort((self.m.A["pet_id"].to_numpy(), -(a["budget"] / self.m.A["p_eff_cost"].to_numpy() if not np.isnan(a["budget"]) else 0), -score))
        picked, cnt = [], {}
        for i in order:
            if not ok[i]: continue
            r = self.m.A.at[i, "Race"]
            if cnt.get(r, 0) < max_per_race:
                picked.append(i); cnt[r] = cnt.get(r, 0) + 1
            if len(picked) >= k: break
        if len(picked) < k:      # complète si la diversité empêche d'atteindre k
            rest = [i for i in order if ok[i] and i not in picked]
            picked += rest[: k - len(picked)]
        recs = []
        for i in picked:
            st, wo = self.m.strengths_and_watchouts(a, self.m.A.iloc[i], D.iloc[i])
            r = self.m.A.iloc[i]
            passed = self.m.rules_passed(a, r, D.iloc[i])
            recs.append({"rang": len(recs) + 1, "pet_id": r["pet_id"], "nom": r["pet_name"], "espece": r["Espece"], "race": r["Race"],
                         "age_ans": float(r["age_years"]), "score": round(float(score[i]), 4), "decision": "OUI",
                         "regles_validees": passed, "points_forts": st[:3], "points_vigilance": wo,
                         "explication": self._texte(True, float(score[i]), float(proba[i]), r["pet_name"], r["Race"], [], passed, st[:3], wo, [], court=True)})
        n = int(ok.sum())
        if n == 0:
            msg = "Aucun animal compatible avec votre profil. " + self.m._blocking_summary(D)
        elif n < k:
            msg = f"Seulement {n} animal(aux) compatible(s) : voici tous ceux qui conviennent."
        else:
            msg = f"Top {k} des animaux les plus adaptés à votre profil."
        out = {"top": recs, "message": msg + note, "n_compatibles": n, "avertissements_profil": warns}
        if consulted_id is not None:
            out["consulte"] = self.decide(adopter, consulted_id)
        return out

    def save(self, path="models/petmatch_algorithm.pkl"):
        joblib.dump(self, path); return path

    @staticmethod
    def load(path="models/petmatch_algorithm.pkl"):
        return joblib.load(path)



# ====================================================================== service (notebook / futur backend)
def _jsonable(o):
    if isinstance(o, dict): return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_jsonable(v) for v in o]
    if isinstance(o, np.generic): return o.item()
    return o


class PetMatchService:
    """Point d'entrée unique : l'utilisateur donne (id adoptant OU profil saisi) + id de l'animal.
    Renvoie un dictionnaire JSON-compatible prêt à être renvoyé par une API."""
    PROFIL_REQUIS = ["Type_Logement", "Budget_Mensuel_DZD", "Heures_Presence_Jour", "Nombre_Enfants", "Experience_Animaux"]

    def __init__(self, model: PetMatchModel, adoptants: pd.DataFrame):
        self.model = model
        self.adoptants = adoptants.set_index("ID_Adoptant", drop=False)

    def verifier(self, pet_id: str, adopter_id: str | None = None, profil: dict | None = None, k: int = 5) -> dict:
        if pet_id not in self.model.m._id2idx:
            return {"erreur": f"Animal introuvable : « {pet_id} ». Vérifiez l'identifiant (ex. P000003)."}
        if profil is None:
            if adopter_id is None:
                return {"erreur": "Fournissez un identifiant d'adoptant OU un profil saisi."}
            if adopter_id not in self.adoptants.index:
                return {"erreur": f"Adoptant introuvable : « {adopter_id} » (ex. ADOPT_0001)."}
            profil = self.adoptants.loc[adopter_id].to_dict()
        profil = dict(profil)
        animal = self.model.m.animals.iloc[self.model.m._id2idx[pet_id]]
        res = self.model.decide(profil, pet_id)
        alt_profile = {**profil, "Espece": animal["Espece"]}        # alternatives : d'abord la même espèce que l'animal choisi
        alt = self.model.recommend(alt_profile, consulted_id=pet_id, k=k)
        res.update({"adoptant": adopter_id or "profil saisi", "alternatives": alt["top"], "message_alternatives": alt["message"]})
        return _jsonable(res)


def afficher(res: dict):
    """Affichage lisible (notebook) du résultat de PetMatchService.verifier."""
    if "erreur" in res:
        print("⚠", res["erreur"]); return
    print(f"Adoptant : {res['adoptant']}   |   Animal : {res['animal']['nom']} ({res['animal']['race']}, {res['animal']['pet_id']})")
    print("=" * 90); print(res["explication"])
    for w in res.get("avertissements_profil", []): print("⚠", w)
    print("\n" + "-" * 90); print("ALTERNATIVES —", res["message_alternatives"])
    for x in res["alternatives"]:
        print(f"\n#{x['rang']}  {x['nom']} ({x['race']}, {x['age_ans']:.1f} an(s))  —  score {x['score']:.0%}")
        for r in x["regles_validees"]: print(f"     ✓ {r}")
        for f in x["points_forts"]: print(f"     + {f}")
        for v in x["points_vigilance"]: print(f"     ! {v}")


# ====================================================================== évaluation + démo
def evaluate(model: PetMatchModel, test: pd.DataFrame, n_rep: int = 5):
    """Décision OUI/NON vs Cible_Compatible sur des adoptants jamais vus (n_rep animaux de la race souhaitée chacun)."""
    rng = np.random.default_rng(123)
    by_race = {r: np.flatnonzero((model.m.animals["Race"] == r).to_numpy()) for r in model.m.animals["Race"].unique()}
    y, p, s = [], [], []
    for _, r in test.iterrows():
        idx = rng.choice(by_race[r["Race"]], n_rep, replace=False)
        saved, model.cfg.use_preference = model.cfg.use_preference, False
        try:
            _, _, _, D, proba, score, ok = model._score_all(r.to_dict(), idx)
        finally:
            model.cfg.use_preference = saved
        y += [int(r["Cible_Compatible"])] * n_rep; p += list(ok.astype(int)); s += list(score)
    y, p, s = np.array(y), np.array(p), np.array(s)
    return dict(accuracy=round(accuracy_score(y, p), 4), precision=round(precision_score(y, p), 4), recall=round(recall_score(y, p), 4),
                f1=round(f1_score(y, p), 4), macro_f1=round(f1_score(y, p, average="macro"), 4), auc=round(roc_auc_score(y, s), 4),
                confusion_matrix=confusion_matrix(y, p, labels=[0, 1]).tolist(), n_paires_test=len(y))


if __name__ == "__main__":
    animals = load_animals("data/petmatch_animals_clean.csv")
    adop = pd.read_csv("data/petmatch_adoptants_clean.csv")
    tr, te = train_test_split(adop, test_size=0.20, stratify=adop["Cible_Compatible"], random_state=SEED)
    cfg = Config(**{k: (tuple(v) if k == "hard_rules" else v) for k, v in json.load(open("models/matching_config_best.json")).items()})

    t = time.time(); model = PetMatchModel(cfg).fit(tr, animals); print(f"Entraînement : {time.time()-t:.0f}s", model.info)
    res = evaluate(model, te); print("TEST (adoptants jamais vus) :", res)

    # Robustesse : tous les adoptants (Top-5), bornes de score, temps
    times, bad = [], 0
    for _, r in adop.iterrows():
        t0 = time.perf_counter(); out = model.recommend(r.to_dict()); times.append(time.perf_counter() - t0)
        bad += sum(not (0 <= x["score"] <= 1) or x["decision"] != "OUI" for x in out["top"])
    robust = {"n_adoptants": len(adop), "violations": bad, "temps_moyen_s": round(float(np.mean(times)), 4), "temps_max_s": round(float(np.max(times)), 4)}
    print("Robustesse :", robust)

    path = model.save()
    re = PetMatchModel.load(path)         # rechargement + test
    r0 = te.iloc[0].to_dict()
    same = re.recommend(r0)["top"][0]["pet_id"] == model.recommend(r0)["top"][0]["pet_id"]
    json.dump({"modele": model.info, "test": res, "robustesse": robust, "rechargement_identique": same},
              open("experiments/algorithm_results.json", "w"), ensure_ascii=False, indent=1)

    # Démo 1 : adoptant du dataset (animal consulté = 1er animal de sa race souhaitée)
    for who in [te.iloc[0], te[te["Type_Logement"] == "Appartement F2"][te["Espece"] == "Dog"].iloc[0]]:
        p = who.to_dict(); pid = animals[animals["Race"] == p["Race"]]["pet_id"].iloc[0]
        out = re.recommend(p, consulted_id=pid)
        print("\n=== Adoptant", p["ID_Adoptant"], "|", p["Type_Logement"], "|", p["Budget_Mensuel_DZD"], "DZD |", p["Heures_Presence_Jour"], "h présence | souhaite", p["Race"])
        print(json.dumps(out["consulte"], ensure_ascii=False, indent=1))
        print(out["message"])
        for x in out["top"]: print(f"  #{x['rang']} {x['nom']} ({x['race']}) score={x['score']} | {x['points_forts'][:1]}")
