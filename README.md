# Calculum

Site web du club de programmation compétitive de l'Université de Montréal.

🔗 **Live:** https://calculum.vicnas.me

## Structure

Le site comporte trois sections principales:

### 📋 Rencontres
- Affiche toutes les rencontres organisées par session (Automne/Hiver/Été)
- Chaque rencontre montre:
  - Date et thème
  - Informations de la session (local, heure)
  - Liste des problèmes avec liens vers les énoncés et solutions
  - Algorithme de la rencontre (affichage pliable avec coloration syntaxique Python)

### 📚 Aide-mémoire
- Compilation compacte de tous les algorithmes
- Format imprimable en 2 colonnes
- Optimisé pour les compétitions (ICPC, etc.)

### 🎉 Événements
- Galerie des activités du club
- Supporte images et vidéos
- Événement le plus récent mis en évidence

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL

### Setup Local

1. **Cloner le repo**
```bash
git clone <repo-url>
cd calculum
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine:
```env
DJANGO_SECRET_KEY=votre-clé-secrète
DJANGO_DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/calculum
DOMAIN=127.0.0.1
```

5. **Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superuser**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic --noinput
```

8. **Lancer le serveur**
```bash
python manage.py runserver
```

Accéder à `http://127.0.0.1:8000/`

## Utilisation

### Ajouter une rencontre

1. Créer le fichier d'algorithme dans `board/meets/YYYY/MM/DD.py`
   ```python
   # Exemple: board/meets/2026/01/23.py
   def dijkstra(graph, start):
       # Votre algorithme ici
       pass
   ```

2. Via l'admin Django (`/admin`):
   - Créer un Meet avec la date correspondante
   - Ajouter un thème (optionnel)
   - La Session sera créée automatiquement selon la date

3. Ajouter des problèmes:
   - Créer des Problems liés au Meet
   - Spécifier: plateforme, lien problème, lien solution

### Sessions automatiques

Les sessions sont déterminées automatiquement par la date:
- **Automne** (septembre-décembre)
- **Hiver** (janvier-avril)  
- **Été** (mai-août)

Par défaut: `AA-3189` à `18:00`

### Ajouter un événement

Via l'admin:
1. Créer un Event (titre + résumé)
2. Ajouter des Media (images/vidéos)

## Déploiement

1. Variables d'environnement requises:
   - `DJANGO_SECRET_KEY`
   - `DATABASE_URL` (auto-configuré par Railway)
   - `DOMAIN`

2. Execution:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
   - `gunicorn project.wsgi:application`

## Architecture

### Modèles

**Meet**: Date, thème, session  
**Problem**: Lien, plateforme, solution  
**Session**: Saison, année, local, heure  
**Event**: Titre, résumé  
**Media**: Fichier (image/vidéo), event associé

## Technologies

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Storage**: Server
- **Frontend**: HTML/CSS/JS vanilla
- **Syntax Highlighting**: Highlight.js
- **Deployment**: Railway + Gunicorn + WhiteNoise

## Contribuer

1. Les modèles sont simples par design - ne pas compliquer
2. Tout en français pour l'interface utilisateur
3. CSS/JS séparés dans `project/static/`
4. Pas d'authentification pour la lecture (admin seulement)

## License

Projet du club Calculum - Université de Montréal
