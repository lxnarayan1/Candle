web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn candle.wsgi:application --bind 0.0.0.0:${PORT:-8080}
