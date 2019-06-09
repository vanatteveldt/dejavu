rm -f dejaviewer/migrations/*.py &&
    rm -f db.sqlite3 &&
    env/bin/python manage.py makemigrations dejaviewer &&
    env/bin/python manage.py migrate &&
    env/bin/python manage.py loaddata dejaviewer/initial_data.yaml  &&
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('wva', 'admin@example.com', 'wva')" | env/bin/python manage.py shell
