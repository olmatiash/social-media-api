python manage.py migrate
docker run -d -p 6379:6379 redis
celery -A social_media_api worker -l INFO
python manage.py runserver

docker-compose build
docker-compose up
