"""
Ponto de entrada serverless para a Vercel usando vercel-wsgi.
"""
import sys
import traceback
from app import app
from vercel_wsgi import handle


def handler(event, context):
    try:
        return handle(event, context, app)
    except Exception as exc:
        print(f"[handler] erro: {exc}", file=sys.stderr)
        traceback.print_exc()
        raise
