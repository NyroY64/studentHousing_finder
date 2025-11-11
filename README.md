
# **Fac Habitat Scraper**

## **Description du Projet**
Ce projet a été créé pour m'aider à trouver un appartement étudiant pour l'année scolaire 2024/2025. Il s'agit d'un scraper Python conçu pour récupérer les informations des résidences disponibles sur le site **Fac Habitat**, en filtrant les résultats selon plusieurs critères tels que le département, la disponibilité, et d'autres informations importantes.

Ce projet est conçu pour être simple, efficace, et extensible pour répondre à d'autres besoins liés à la recherche d'appartements étudiants.

---

## **Fonctionnalités Actuelles**

- **Scraping des Résidences :**
  - Extraction des adresses et liens des résidences disponibles sur le site **Fac Habitat**.
  - Ignoration des résidences provenant de **Logifac**.

- **Filtrage par Département :**
  - Filtre les résultats en fonction des départements sélectionnés (par exemple, Paris et les départements voisins).

- **Vérification de Disponibilité :**
  - Analyse de la disponibilité des résidences directement à partir des informations fournies (statuts pris en compte : **"Disponible"** et **"Disponibilité à venir"**).

- **Exportation des Résultats :**
  - Enregistre les résultats des résidences disponibles dans un fichier JSON (`data/residences.json`).

- **Logs et Débogage :**
  - Toutes les erreurs et informations d'exécution sont enregistrées dans un fichier de logs (`data/logs/scraper.log`).

---

## **Logique et Fonctionnement**

1. **Scraper les Résidences :**
   - Le programme utilise **requests** pour envoyer des requêtes HTTP au site **Fac Habitat**.
   - Les données HTML sont analysées avec **BeautifulSoup** pour extraire les résidences, leurs adresses et leurs liens.

2. **Filtrage par Département :**
   - Le programme compare le code postal des adresses aux départements spécifiés dans le fichier `config.py`.

3. **Vérification de la Disponibilité :**
   - Chaque lien de résidence est analysé pour trouver l'iframe contenant les informations de disponibilité.
   - Le programme détecte deux statuts spécifiques : **"Disponible"** et **"Disponibilité à venir"**.

4. **Exportation :**
   - Les résidences disponibles sont sauvegardées dans un fichier JSON pour un usage futur.

---

## **Installation**

### **Prérequis**
- Python 3.7 ou une version plus récente.

### **Étapes d'installation**

1. Clonez ce repository :
   ```bash
   git clone https://github.com/NyroY64/fac_habitat_scraper.git
   cd fac_habitat_scraper
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer le scraper :
   ```bash
   python main.py
   ```

---

## **Résultats**

- Les résultats des résidences disponibles sont sauvegardés dans `data/residences.json`.
- Le fichier de logs (`data/logs/scraper.log`) contient les détails de l'exécution.

---

## **Améliorations Futures (Roadmap)**

### **Version à venir (v2.0)**

0. **Calculateur de Distance :**
   - Ajout des notification lorsque une residence devient disponible.
   - Utilisation d'API de géocodage comme **Google Maps API** ou **OpenStreetMap**.


1. **Calculateur de Distance :**
   - Ajout d'un calculateur de distance entre chaque résidence et une adresse donnée (ex : université).
   - Utilisation d'API de messagerie comme **sendgrid** .

2. **Calculateur de Trajet (Transport en Commun) :**
   - Intégration d'API de transport en commun pour calculer le trajet (temps et coûts) vers une adresse cible.

3. **Filtrage par Type de Logement :**
   - Prise en compte du type de logement (T1, T2, colocations, etc...).

4. **Automatisation du Processus d'Inscription :**
   - Automatisation du remplissage et de l'envoi des formulaires de demande pour les résidences disponibles.

---

## **Contribution**

Les contributions sont les bienvenues pour améliorer ce projet.

### **Comment contribuer ?**
1. Fork ce repository.
2. Créez une branche pour vos modifications :
   ```bash
   git checkout -b nouvelle-fonctionnalite
   ```
3. Faites vos modifications et committez-les :
   ```bash
   git commit -m "Ajout d'une nouvelle fonctionnalité"
   ```
4. Poussez votre branche :
   ```bash
   git push origin nouvelle-fonctionnalite
   ```
5. Créez une Pull Request.

---

## **Tests**

Pour exécuter les tests unitaires :
```bash
python -m unittest discover -s tests
```

Les tests incluent :
- Vérification des URLs (`utils.py`).
- Tests pour la logique de scraping.

---

## **Auteur**

- **Josef**  
  Étudiant en développement informatique, passionné par l'automatisation et l'analyse de données.
