REMOTE=calculum@srv.aediroum.ca
REMOTE_DIR=/srv/calculum

# Setup initial (UNE SEULE FOIS) - local
setup:
	@echo "⚠️  Setup initial - À faire UNE SEULE FOIS"
	createdb calculum 2>/dev/null || echo "Database 'calculum' already exists"
	python manage.py migrate
	python manage.py loaddata fixtures/calculum_data.json
	@echo "✅ Setup terminé."

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