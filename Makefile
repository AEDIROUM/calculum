REMOTE=calculum@srv.aediroum.ca

deploy:
	ssh ${REMOTE} \
		"cd /srv/calculum && \
		git pull && \
		source venv/bin/activate && \
		pip install -r requirements.txt && \
		python manage.py migrate && \
		python manage.py collectstatic --noinput && \
		sudo systemctl restart calculum"
