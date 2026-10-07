"""
Vercel serverless entry point for Django application.
This file is used by @vercel/python to serve the Django WSGI application.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "birthday_project.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Vercel handler
def handler(request, context):
    """
    Vercel serverless function handler.
    Converts the Vercel request to WSGI environ and returns the response.
    """
    from io import BytesIO
    from django.core.handlers.wsgi import WSGIRequest
    
    # Build WSGI environ from Vercel request
    environ = {
        "REQUEST_METHOD": request.get("method", "GET"),
        "SCRIPT_NAME": "",
        "PATH_INFO": request.get("path", "/"),
        "QUERY_STRING": request.get("queryString", ""),
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": BytesIO(
            request.get("body", b"") if isinstance(request.get("body"), bytes)
            else (request.get("body", "").encode() if request.get("body") else b"")
        ),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": True,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    
    # Add headers
    for key, value in (request.get("headers") or {}).items():
        key = key.upper().replace("-", "_")
        if key == "CONTENT_TYPE":
            environ["CONTENT_TYPE"] = value
        elif key == "CONTENT_LENGTH":
            environ["CONTENT_LENGTH"] = value
        else:
            environ[f"HTTP_{key}"] = value
    
    # Capture response
    response_status = []
    response_headers = []
    response_body = []
    
    def start_response(status, headers, exc_info=None):
        response_status.append(status)
        response_headers.extend(headers)
    
    # Run the WSGI application
    result = application(environ, start_response)
    
    # Collect body
    for chunk in result:
        if isinstance(chunk, bytes):
            response_body.append(chunk)
        else:
            response_body.append(chunk.encode())
    
    body = b"".join(response_body)
    
    # Parse status code
    status_code = int(response_status[0].split()[0]) if response_status else 200
    
    # Build headers dict
    headers_dict = {}
    for key, value in response_headers:
        headers_dict[key] = value
    
    return {
        "statusCode": status_code,
        "headers": headers_dict,
        "body": body.decode("utf-8", errors="replace"),
    }