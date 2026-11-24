"""Catalogue des animaux du refuge (données de départ).
Une ligne = un animal. La photo est un fichier du FRONT : frontend/public<img>  (ex. /animals/cats/siamese.jpg).
La race doit exister dans les données d'entraînement du modèle (voir GET /api/races).

Pour AJOUTER un animal : 1) copiez la photo dans frontend/public/animals/<dossier>/,
2) ajoutez son crédit dans frontend/src/lib/credits.json, 3) ajoutez une ligne ici (ou POST /api/animals).
"""
# (nom, espece, race, age, taille, energie 1-5, wilaya, association, img, maladie_chronique, comportement_difficile)
CATALOG = [
    # ── Chiens ────────────────────────────────────────────────────────────────
    ("Maya",     "chien", "Labrador Retriever", 3, "grande",  4, "Blida",       "LPAA",    "/animals/dogs/labrador_retriever.jpg", False, False),
    ("Bouly",    "chien", "French Bulldog",     2, "petite",  2, "Alger",       "El Rifk", "/animals/dogs/french_bulldog.jpg",     False, False),
    ("Soleil",   "chien", "Golden Retriever",   5, "grande",  4, "Oran",        "El Rifk", "/animals/dogs/golden_retriever.jpg",   False, False),
    ("Mochi",    "chien", "Mixed Breed",        3, "moyenne", 3, "Tipaza",      "El Rifk", "/animals/dogs/mixed_breed.jpg",        False, False),
    ("Coco",     "chien", "Poodle",             4, "petite",  3, "Constantine", "LPAA",    "/animals/dogs/poodle.jpg",             False, False),
    ("Biscuit",  "chien", "Beagle",             8, "moyenne", 3, "Oran",        "LPAA",    "/animals/dogs/beagle.jpg",             False, False),
    ("Tyson",    "chien", "Boxer",              4, "grande",  5, "Sétif",       "LPAA",    "/animals/dogs/boxer.jpg",              False, True),
    ("Rocky",    "chien", "Rottweiler",         5, "grande",  3, "Annaba",      "El Rifk", "/animals/dogs/rottweiler.jpg",         False, True),
    ("Pepa",     "chien", "Chihuahua",          6, "petite",  2, "Alger",       "El Rifk", "/animals/dogs/chihuahua.jpg",          False, False),
    # ── Chats ─────────────────────────────────────────────────────────────────
    ("Luna",     "chat",  "Domestic Shorthair", 2, "petite",  2, "Alger",       "El Rifk", "/animals/cats/domestic_shorthair.jpg", False, False),
    ("Pixel",    "chat",  "Siamese",            1, "petite",  4, "Blida",       "LPAA",    "/animals/cats/siamese.jpg",            False, False),
    ("Simba",    "chat",  "Maine Coon",         1, "moyenne", 4, "Oran",        "El Rifk", "/animals/cats/maine_coon.jpg",         False, False),
    ("Cléo",     "chat",  "Abyssinian",         3, "petite",  4, "Alger",       "LPAA",    "/animals/cats/abyssinian.jpg",         False, False),
    ("Tigre",    "chat",  "Bengal",             2, "moyenne", 5, "Oran",        "El Rifk", "/animals/cats/bengal.jpg",             False, False),
    ("Nuage",    "chat",  "British Shorthair",  4, "moyenne", 2, "Constantine", "El Rifk", "/animals/cats/british_shorthair.jpg",  False, False),
    ("Mimine",   "chat",  "Domestic Longhair",  9, "moyenne", 1, "Blida",       "LPAA",    "/animals/cats/domestic_longhair.jpg",  True,  False),
    ("Ragda",    "chat",  "Ragdoll",            3, "moyenne", 2, "Tizi Ouzou",  "LPAA",    "/animals/cats/ragdoll.jpg",            False, False),
    ("Ramsès",   "chat",  "Sphynx",             2, "petite",  3, "Alger",       "El Rifk", "/animals/cats/sphynx.jpg",             False, False),
    # ── Lapins ────────────────────────────────────────────────────────────────
    ("Noisette", "lapin", "Holland Lop",        1, "petite",  2, "Alger",       "El Rifk", "/animals/rabbits/holland_lop.jpg",     False, False),
    ("Velours",  "lapin", "Rex",                2, "moyenne", 2, "Blida",       "LPAA",    "/animals/rabbits/rex.jpg",             False, False),
    ("Grisou",   "lapin", "Flemish Giant",      3, "grande",  3, "Tizi Ouzou",  "El Rifk", "/animals/rabbits/flemish_giant.jpg",   False, False),
    # ── Oiseaux ───────────────────────────────────────────────────────────────
    ("Kiwi",     "oiseau", "Budgerigar (Budgie)",  1,  "petite",  3, "Alger",   "El Rifk", "/animals/birds/budgerigar_budgie.jpg", False, False),
    ("Cerise",   "oiseau", "Lovebird",             1,  "petite",  3, "Tipaza",  "LPAA",    "/animals/birds/lovebird.jpg",          False, False),
    ("Zouzou",   "oiseau", "Canary",               2,  "petite",  2, "Blida",   "El Rifk", "/animals/birds/canary.jpg",            False, False),
    ("Jaco",     "oiseau", "African Grey Parrot",  7,  "moyenne", 4, "Oran",    "LPAA",    "/animals/birds/african_grey_parrot.jpg", False, True),
    ("Arlequin", "oiseau", "Macaw",                10, "grande",  4, "Annaba",  "LPAA",    "/animals/birds/macaw.jpg",             False, True),
    # ── Poissons ──────────────────────────────────────────────────────────────
    ("Bleu",     "poisson", "Betta",  1, "petite", 1, "Alger",  "El Rifk", "/animals/fish/betta.jpg",  False, False),
    ("Flash",    "poisson", "Guppy",  1, "petite", 2, "Sétif",  "LPAA",    "/animals/fish/guppy.jpg",  False, False),
    ("Néon",     "poisson", "Tetra",  1, "petite", 2, "Oran",   "El Rifk", "/animals/fish/tetra.jpg",  False, False),
    # ── Reptiles ──────────────────────────────────────────────────────────────
    ("Drago",    "reptile", "Bearded Dragon",           2,  "petite",  2, "Oran",   "LPAA",    "/animals/reptiles/bearded_dragon.jpg",           False, False),
    ("Kaa",      "reptile", "Ball Python",              4,  "moyenne", 1, "Alger",  "El Rifk", "/animals/reptiles/ball_python.jpg",              False, False),
    ("Franklin", "reptile", "Red-Eared Slider Turtle",  10, "petite",  1, "Blida",  "LPAA",    "/animals/reptiles/red_eared_slider_turtle.jpg",  False, False),
    # ── Petits mammifères ─────────────────────────────────────────────────────
    ("Pompon",   "mammifere", "Hamster",     1, "petite", 3, "Alger",       "El Rifk", "/animals/small_mammals/hamster.jpg",     False, False),
    ("Caramel",  "mammifere", "Guinea Pig",  2, "petite", 2, "Sétif",       "LPAA",    "/animals/small_mammals/guinea_pig.jpg",  False, False),
    ("Zorro",    "mammifere", "Ferret",      3, "petite", 4, "Oran",        "LPAA",    "/animals/small_mammals/ferret.jpg",      False, True),
    ("Cendre",   "mammifere", "Chinchilla",  3, "petite", 3, "Constantine", "El Rifk", "/animals/small_mammals/chinchilla.jpg",  False, False),
    ("Sable",    "mammifere", "Gerbil",      1, "petite", 4, "Tipaza",      "El Rifk", "/animals/small_mammals/gerbil.jpg",      False, False),
]
