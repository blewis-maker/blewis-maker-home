# Import the appropriate settings based on environment
import os

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'ecommerce.settings.production':
    from .production import *
else:
    from .development import *