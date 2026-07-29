web: python manage.py migrate --noinput && python manage.py setup_admin || true && gunicorn myblog.wsgi --timeout 120 --bind 0.0.0.0:$PORT
