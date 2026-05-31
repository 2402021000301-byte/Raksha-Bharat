"""
WSGI config for Raksha Bharat project.
Production deployment configuration.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raksha_bharat.settings')

application = get_wsgi_application()
