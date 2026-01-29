REMOTE=calculum@srv.aediroum.ca
REMOTE_DIR=/srv/calculum

# Initial setup on remote (run once)
setup:
	@echo "📦 Initial setup..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && \
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
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && pkill -f 'gunicorn.*project.wsgi'" 2>/dev/null || true
	@echo "📥 Pulling latest code..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && git pull origin main" | grep -E "(Already up to date|Updating|Fast-forward)" || true
	@echo "📦 Installing dependencies..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && pip install -q -r requirements.txt"
	@echo "🗄️  Running migrations..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py migrate --noinput" | grep -v "No migrations to apply" || echo "  ✓ No migrations needed"
	@echo "📁 Collecting static files..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py collectstatic --noinput" | tail -1
	@echo "🧹 Cleaning up orphaned media files..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && python manage.py cleanup_media_files 2>/dev/null" || echo "  ⊘ Cleanup skipped (command not installed yet)"
	@echo "🌐 Starting server..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source venv/bin/activate && nohup gunicorn project.wsgi:application --bind 0.0.0.0:8000 > server.log 2>&1 & sleep 1"
	@echo "✅ Deployed!"

# Stop server
stop:
	@echo "🛑 Stopping server..."
	@ssh $(REMOTE) "pkill -f 'gunicorn.*project.wsgi'" 2>/dev/null && echo "✅ Stopped" || echo "⊘ No server running"

# View logs
logs:
	@ssh $(REMOTE) "tail -f $(REMOTE_DIR)/server.log"

# Local development
runserver:
	@python manage.py runserver

# Backup database to fixtures
backup:
	@echo "💾 Backing up database to fixtures..."
	@python manage.py dumpdata --indent 2 > fixtures/calculum_data.json
	@echo "✅ Backup complete: fixtures/calculum_data.json"