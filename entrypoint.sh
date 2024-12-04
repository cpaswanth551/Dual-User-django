#!/bin/bash

set -e


set -x

chmod +x "$0"


echo "Applying database migrations..."
python manage.py migrate --noinput 

echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="superadmin").exists():
    User.objects.create_superuser("superadmin", "admin@knackforge.com", "admin")
    print("Superuser created.")
else:
    print("Superuser already exists.")
END

exec "$@"