release: python manage.py migrate
web: gunicorn pgadmin_config.wsgi:application --bind 0.0.0.0:$PORT --log-file -
