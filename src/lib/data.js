// Données de démonstration : utilisées tant que l'API FastAPI (/api/animals) n'est pas branchée.
export const ANIMALS = [
  { id: 1, nom: 'Luna',    espece: 'chat',  age: 2, taille: 'petite',  energie: 2, wilaya: 'Alger',   asso: 'El Rifk', img: '/pets/cat.png' },
  { id: 2, nom: 'Rex',     espece: 'chien', age: 4, taille: 'grande',  energie: 4, wilaya: 'Blida',   asso: 'LPAA',    img: '/pets/dog-paw.png' },
  { id: 3, nom: 'Biscuit', espece: 'chien', age: 1, taille: 'moyenne', energie: 5, wilaya: 'Oran',    asso: 'LPAA',    img: '/pets/puppy.png' },
  { id: 4, nom: 'Noisette',espece: 'lapin', age: 1, taille: 'petite',  energie: 2, wilaya: 'Alger',   asso: 'El Rifk', img: '/pets/rabbit.png' },
  { id: 5, nom: 'Mochi',   espece: 'chien', age: 3, taille: 'moyenne', energie: 3, wilaya: 'Tipaza',  asso: 'El Rifk', img: '/pets/shiba.png' },
  { id: 6, nom: 'Pixel',   espece: 'chat',  age: 1, taille: 'petite',  energie: 3, wilaya: 'Blida',   asso: 'LPAA',    img: '/pets/puppy-kitten.png' },
]

export const ESPECES = [
  { value: 'tous', label: 'Tous' },
  { value: 'chat', label: 'Chats' },
  { value: 'chien', label: 'Chiens' },
  { value: 'lapin', label: 'Lapins' },
]

export const WILAYAS = ['Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa', 'Biskra', 'Béchar', 'Blida', 'Bouira', 'Tamanrasset', 'Tébessa', 'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger', 'Djelfa', 'Jijel', 'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma', 'Constantine', 'Médéa', 'Mostaganem', "M'Sila", 'Mascara', 'Ouargla', 'Oran', 'El Bayadh', 'Illizi', 'Bordj Bou Arréridj', 'Boumerdès', 'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued', 'Khenchela', 'Souk Ahras', 'Tipaza', 'Mila', 'Aïn Defla', 'Naâma', 'Aïn Témouchent', 'Ghardaïa', 'Relizane', 'Timimoun', 'Bordj Badji Mokhtar', 'Ouled Djellal', 'Béni Abbès', 'In Salah', 'In Guezzam', 'Touggourt', 'Djanet', "El M'Ghair", 'El Meniaa']
