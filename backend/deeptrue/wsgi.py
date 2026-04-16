"""
WSGI config for deeptrue project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deeptrue.settings')

application = get_wsgi_application()

