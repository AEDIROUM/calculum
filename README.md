# Calculum

Site web du club de programmation compétitive de l'Université de Montréal.

🔗 **Live:** https://calculum.vicnas.me

## Quick Start

**Requirements**: Python 3.10+, PostgreSQL

```bash
# Setup
make setup
make runserver
```

Visit `http://127.0.0.1:8000/admin` to add content.

## What's Here

- **📋 Meets**: Competitions by session with problems & solutions
- **📚 Cheatsheet**: Printable algorithm reference
- **🎉 Events**: Club activities & gallery

## Adding Content

### Meets
1. Create algorithm file: `board/meets/YYYY/MM/DD.py`
2. Add Meet in admin with matching date
3. Add Problems (link + platform)

### Events
1. Create Event in admin
2. Add Media (images/videos)

## Environment

Create `.env`:
```env
SECRET_KEY=your-key-here
DEBUG=True
DOMAIN=127.0.0.1
```

Database defaults to PostgreSQL locally, SQLite on remote if `DATABASE_URL` not set.

## Tech Stack

Django 5.0 • PostgreSQL • Vanilla HTML/CSS/JS • Gunicorn
