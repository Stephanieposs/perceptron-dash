from app import app
from vercel_wsgi import handler


def main(request, *args, **kwargs):
    return handler(app, request, *args, **kwargs)
