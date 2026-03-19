SHELL := /bin/bash
REMOTE=calculum@srv.aediroum.ca
REMOTE_DIR=/srv/calculum

# Initial setup on remote (run once)
setup:
	@echo "📦 Initial setup..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && \
		python3 -m venv calculum-venv/venv && \
		source calculum-venv/venv/bin/activate && \
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
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source calculum-venv/venv/bin/activate && pip install -q -r requirements.txt"
	@echo "🗄️  Running migrations..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source calculum-venv/venv/bin/activate && python manage.py migrate --noinput" | grep -v "No migrations to apply" || echo "  ✓ No migrations needed"
	@echo "📁 Collecting static files..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source calculum-venv/venv/bin/activate && python manage.py collectstatic --noinput" | tail -1
	@echo "🧹 Cleaning up orphaned media files..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source calculum-venv/venv/bin/activate && python manage.py cleanup_media_files 2>/dev/null" || echo "  ⊘ Cleanup skipped (command not installed yet)"
	@echo "🌐 Starting server..."
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && calculum-venv/venv/bin/gunicorn project.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 2 --max-requests 1000 --max-requests-jitter 50 --graceful-timeout 30 --access-logfile $(REMOTE_DIR)/server.log --error-logfile $(REMOTE_DIR)/server.log --log-level debug --daemon --pid $(REMOTE_DIR)/gunicorn.pid --log-file $(REMOTE_DIR)/server.log"
	@echo "🔄 Restarting monitor service for safety..."
	@ssh $(REMOTE) "systemctl --user restart calculum-monitor.service"
	@echo "✅ Deployed!"

# Stop server
stop:
	@echo "🛑 Stopping server..."
	@ssh $(REMOTE) "pkill -f 'gunicorn.*project.wsgi'" 2>/dev/null && echo "✅ Stopped" || echo "⊘ No server running"

# View logs
logs:
	@ssh $(REMOTE) "tail -f $(REMOTE_DIR)/server.log" | grep -v "/static/"

# Monitor service status
monitor-status:
	@echo "📊 Monitoring service status..."
	@ssh $(REMOTE) "systemctl --user status calculum-monitor.service"

# View monitor logs
monitor-logs:
	@echo "📋 Monitoring service logs..."
	@ssh $(REMOTE) "journalctl --user -u calculum-monitor.service -n 50 --no-pager"

# View restart history
restart-history:
	@echo "🔄 Server restart history..."
	@ssh $(REMOTE) "cat $(REMOTE_DIR)/restart.log 2>/dev/null" || echo "No restarts logged yet"

# Restart monitor service
monitor-restart:
	@echo "🔄 Restarting monitor service..."
	@ssh $(REMOTE) "systemctl --user restart calculum-monitor.service"
	@echo "✅ Monitor restarted"

debug:
	@echo "🔄 Restarting with DEBUG=True..."
	@ssh $(REMOTE) "systemctl --user stop calculum-monitor.service; pkill -f 'gunicorn.*project.wsgi'" 2>/dev/null || true
	@ssh $(REMOTE) "cd $(REMOTE_DIR) && source calculum-venv/venv/bin/activate && DEBUG=True calculum-venv/venv/bin/python manage.py runserver"
