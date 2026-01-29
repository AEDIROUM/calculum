
# Calculum

Site du club de programmation compétitive de l'Université de Montréal.

🔗 **En ligne :** https://calculum.aediroum.ca

## Démarrage rapide

```bash
python manage.py runserver
# Rendez-vous sur http://127.0.0.1:8000/admin
```

## Important

**Si vous modifiez les modèles**, créez les migrations avant de push :
```bash
python manage.py makemigrations
```

Le déploiement automatique vérifie que tout est ok, donc les migrations doivent être synchronisées avec les modèles.

## Contribuer

### Ajouter du contenu sur le site

Tout le contenu est géré via **Django Admin** (`/admin`) :

- **📚 Cheatsheet** → Ajouter des algorithmes par catégorie
- **📋 Meets** → Créer des compétitions avec des problèmes
- **🎉 Événements** → Publier des événements du club & médias

Poussez sur la branche `main` pour déployer automatiquement. Le site vérifie la santé avant de déployer.

## Stack technique

Django 5.0 • SQLite • HTML/CSS/JS

---

**Contributions bienvenues !** Ajoutez des algorithmes, des événements ou corrigez des bugs—tout se fait via le panneau d’administration du site.
(Login nécessaire)