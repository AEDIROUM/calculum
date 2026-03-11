# Calculum

Site du club de programmation compétitive de l'Université de Montréal.

**En ligne :** https://calculum.aediroum.ca

## Emplacement des fichiers frontend

- **Templates HTML :**
  - Les templates HTML se trouvent dans `project/templates/`

- **Fichiers CSS :**
  - Les fichiers CSS se trouvent dans `project/static/css/`

- **Fichiers JavaScript :**
  - Les fichiers JavaScript se trouvent dans `project/static/js/`
  - JS additionnel pour l'admin : `project/static/admin/js/algorithm_codemirror.js`

## Contribuer

### Ajouter du contenu sur le site

Tout le contenu est géré via **Django Admin** :

- **Cheatsheet** → Ajouter des algorithmes par catégorie
- **Meets** → Créer des compétitions avec des problèmes
- **Évènements** → Publier des évènements du club & médias

**Si vous modifiez les modèles**, créez les migrations avant de push :
```bash
python manage.py makemigrations
```

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createcachetable
python manage.py runserver
```

Le déploiement automatique vérifie que tout est ok.

## Stack technique

Django 5.0 • SQLite • HTML/CSS/JS
