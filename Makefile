REMOTE=calculum@srv.aediroum.ca
REMOTE_DIR=/srv/calculum

# Initial setup on remote (run once)
setup:
	@echo "📦 Initial setup..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && \
		python3 -m venv venv && \
		source venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt && \
		python manage.py migrate && \
		python manage.py loaddata fixtures/calculum_data.json && \
		python manage.py collectstatic --noinput"
	@echo "✅ Setup complete"

# Deploy updates
deploy:
	@echo "🚀 Deploying..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && \
		pkill -f 'gunicorn' || pkill -f 'python manage.py runserver' || true && \
		git pull origin main && \
		source venv/bin/activate && \
		pip install -r requirements.txt && \
		python manage.py migrate && \
		python manage.py collectstatic --noinput && \
		nohup gunicorn project.wsgi:application --bind 0.0.0.0:8000 > server.log 2>&1 &"
	@echo "✅ Deployed!"

# Pull latest code
pull:
	@echo "📥 Pulling latest code..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && git pull origin main"
	@echo "✅ Pull complete"

# Stop server
stop:
	@echo "🛑 Stopping server..."
	ssh $(REMOTE) "pkill -f 'gunicorn' || pkill -f 'python manage.py runserver' || echo 'No server running'"
	@echo "✅ Stopped"

# View logs
logs:
	ssh $(REMOTE) "tail -f $(REMOTE_DIR)/server.log"

# Local development
runserver:
	python manage.py runserver