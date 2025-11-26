from app import app
from asgiref.wsgi import WsgiToAsgi

# Converte sua app Flask (WSGI) para ASGI
handler = WsgiToAsgi(app)

