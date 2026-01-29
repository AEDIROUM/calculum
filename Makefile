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
	-ssh $(REMOTE) "cd $(REMOTE_DIR) && pkill -f 'gunicorn.*project.wsgi'"
	@echo "📥 Pulling latest code..."
	ssh $(REMOTE) "cd $(REMOTE_DIR) && git pull origin main"
	ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && pip install -r requirements.txt"
	ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py migrate"
	ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py collectstatic --noinput"
	@echo "🧹 Cleaning up orphaned media files..."
	-ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py cleanup_media_files 2>/dev/null || echo '  ⊘ Cleanup skipped (command not installed yet)'"
	ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && nohup gunicorn project.wsgi:application --bind 0.0.0.0:8000 > server.log 2>&1 & sleep 1"
	@echo "✅ Deployed!"

# Stop server
stop:
	@echo "🛑 Stopping server..."
	ssh $(REMOTE) "pkill -f 'python manage.py runserver' || echo 'No server running'"
	@echo "✅ Stopped"

# View logs
logs:
	ssh $(REMOTE) "tail -f $(REMOTE_DIR)/server.log"

# Local development
runserver:
	python manage.py runserver