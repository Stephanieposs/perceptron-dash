"""
Ponto de entrada serverless para a Vercel.
Expõe a app Flask (WSGI) diretamente; Vercel Python lida com WSGI.
"""
import sys
import traceback

try:
    from app import app as application
except Exception as exc:  # log erro de import para aparecer nos logs da Vercel
    print(f"[import] erro ao carregar app: {exc}", file=sys.stderr)
    traceback.print_exc()
    raise

# Vercel detecta `app` como callable WSGI
app = application
# Alias opcional
handler = application
