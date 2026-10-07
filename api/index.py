"""
Vercel serverless entry point for Django application.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "birthday_project.settings")

# Initialize Django once
import django
django.setup(set_prefix=False)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()