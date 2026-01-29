REMOTE=calculum@srv.aediroum.ca
REMOTE_DIR=/srv/calculum

# Initialisation du remote (UNE SEULE FOIS AVANT setup)
init:
	@echo "📦 Initialisation du remote..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && \
		if [ -d .git ]; then git pull; else git init && git remote add origin https://github.com/AEDIROUM/calculum.git && git pull origin main; fi && \
		python3 -m venv venv && \
		source venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt"
	@echo "✅ Remote initialisé."

# Setup initial sur le REMOTE (UNE SEULE FOIS)
setup:
	@echo "⚠️  Setup initial du remote - À faire UNE SEULE FOIS"
	ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py migrate && python manage.py loaddata fixtures/calculum_data.json"
	@echo "✅ Setup terminé sur le remote."

# Pull les changements
pull:
	@echo "📥 Pull sur le remote..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && git pull"
	@echo "✅ Pull terminé."

# Déploiement normal (SANS loaddata)
deploy:
	@echo "🚀 Déploiement..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && \
		pkill -f 'python manage.py runserver' || true && \
		sleep 1 && \
		git pull && \
		source venv/bin/activate && \
		pip install -r requirements.txt && \
		python manage.py migrate && \
		python manage.py collectstatic --noinput && \
		nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &"
	@echo "✅ Déployé!"

# Arrêter le serveur
stop:
	ssh $(REMOTE) "pkill -f 'python manage.py runserver'"

# Logs
logs:
	ssh $(REMOTE) "tail -f $(REMOTE_DIR)/server.log"

# Dev local
runserver:
	python manage.py runserver