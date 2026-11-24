// Données de démonstration : utilisées tant que l'API FastAPI (/api/animals) n'est pas branchée.
export const ANIMALS = [
  { id: 1, nom: 'Luna',     espece: 'chat',  race: 'Domestic Shorthair', age: 2, taille: 'petite',  energie: 2, wilaya: 'Alger',  asso: 'El Rifk', img: '/animals/cats/domestic_shorthair.jpg', nb_commentaires: 0 },
  { id: 2, nom: 'Rex',      espece: 'chien', race: 'Labrador Retriever', age: 4, taille: 'grande',  energie: 4, wilaya: 'Blida',  asso: 'LPAA',    img: '/animals/dogs/labrador_retriever.jpg', nb_commentaires: 0 },
  { id: 3, nom: 'Biscuit',  espece: 'chien', race: 'Beagle',             age: 8, taille: 'moyenne', energie: 3, wilaya: 'Oran',   asso: 'LPAA',    img: '/animals/dogs/beagle.jpg',             nb_commentaires: 0 },
  { id: 4, nom: 'Noisette', espece: 'lapin', race: 'Holland Lop',        age: 1, taille: 'petite',  energie: 2, wilaya: 'Alger',  asso: 'El Rifk', img: '/animals/rabbits/holland_lop.jpg',     nb_commentaires: 0 },
  { id: 5, nom: 'Mochi',    espece: 'chien', race: 'Mixed Breed',        age: 3, taille: 'moyenne', energie: 3, wilaya: 'Tipaza', asso: 'El Rifk', img: '/animals/dogs/mixed_breed.jpg',        nb_commentaires: 0 },
  { id: 6, nom: 'Pixel',    espece: 'chat',  race: 'Siamese',            age: 1, taille: 'petite',  energie: 4, wilaya: 'Blida',  asso: 'LPAA',    img: '/animals/cats/siamese.jpg',            nb_commentaires: 0 },
]

// Les 7 espèces gérées par le modèle PetMatch (clé = valeur renvoyée par l'API)
export const ESPECES = ['tous', 'chat', 'chien', 'lapin', 'oiseau', 'poisson', 'reptile', 'mammifere'].map((value) => ({ value }))
export const EMOJI = { chat: '🐱', chien: '🐶', lapin: '🐰', oiseau: '🐦', poisson: '🐠', reptile: '🦎', mammifere: '🐹' }

export const WILAYAS = ['Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa', 'Biskra', 'Béchar', 'Blida', 'Bouira', 'Tamanrasset', 'Tébessa', 'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger', 'Djelfa', 'Jijel', 'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma', 'Constantine', 'Médéa', 'Mostaganem', "M'Sila", 'Mascara', 'Ouargla', 'Oran', 'El Bayadh', 'Illizi', 'Bordj Bou Arréridj', 'Boumerdès', 'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued', 'Khenchela', 'Souk Ahras', 'Tipaza', 'Mila', 'Aïn Defla', 'Naâma', 'Aïn Témouchent', 'Ghardaïa', 'Relizane', 'Timimoun', 'Bordj Badji Mokhtar', 'Ouled Djellal', 'Béni Abbès', 'In Salah', 'In Guezzam', 'Touggourt', 'Djanet', "El M'Ghair", 'El Meniaa']
