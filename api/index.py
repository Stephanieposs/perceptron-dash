"""
Ponto de entrada para a função serverless na Vercel.
Expõe a app Flask como WSGI callable; o runtime da Vercel detecta `app`.
"""
from app import app

# Para compatibilidade explícita (alguns exemplos usam `handler`):
handler = app
