
# Calculum

Site du club de programmation compétitive de l'Université de Montréal.


## Emplacement des fichiers frontend

- **Templates HTML :**
	- Les templates HTML se trouvent dans `project/templates/`

- **Fichiers CSS :**
	- Les fichiers CSS se trouvent dans `project/static/css/`

- **Fichiers JavaScript :**
	- Les fichiers JavaScript se trouvent dans `project/static/js/`
	- JS additionnel pour l'admin : `project/static/admin/js/algorithm_codemirror.js`

🔗 **En ligne :** https://calculum.aediroum.ca


## Contribuer

### Ajouter du contenu sur le site

Tout le contenu est géré via **Django Admin** (`/admin`) :

- **📚 Cheatsheet** → Ajouter des algorithmes par catégorie
- **📋 Meets** → Créer des compétitions avec des problèmes
- **🎉 Événements** → Publier des événements du club & médias

## Important

**Si vous modifiez les modèles**, créez les migrations avant de push :
```bash
python manage.py makemigrations
```

Le déploiement automatique vérifie que tout est ok.

## Stack technique

Django 5.0 • SQLite • HTML/CSS/JS