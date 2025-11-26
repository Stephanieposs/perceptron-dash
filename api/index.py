"""
Ponto de entrada serverless para a Vercel.
Exponha um ASGI callable chamado `app`. O Flask (WSGI) é adaptado via asgiref.
"""
from asgiref.wsgi import WsgiToAsgi
from app import app as flask_app

# Vercel espera um callable ASGI chamado `app`
app = WsgiToAsgi(flask_app)

# Alias opcional para compatibilidade
handler = app
