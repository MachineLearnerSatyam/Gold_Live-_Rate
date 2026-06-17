import os
from django.core.asgi import get_asgi_application

# 1. Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gold_project.settings')

# 2. Initialize the standard Django ASGI application
django_asgi_app = get_asgi_application()

# 3. Import your FastAPI app instance
from gold_project.fastapi_app import app as fastapi_asgi_app

# 4. Core routing function to split traffic
async def application(scope, receive, send):
    if scope['type'] == 'http' and scope['path'].startswith('/api'):
        await fastapi_asgi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)