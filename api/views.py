"""
Simple test views for Vercel deployment verification.
"""
from datetime import datetime
from django.http import HttpResponse


def index(request):
    """Simple test view to verify Vercel deployment."""
    now = datetime.now()
    html = f'''
    <html>
        <head>
            <title>RunRaids TCG - Vercel Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                .success {{ color: #28a745; }}
                .info {{ color: #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">🎮 RunRaids TCG</h1>
                <h2>✅ Vercel Deployment Successful!</h2>
                <p class="info">The current time is: <strong>{now}</strong></p>
                <p>Django is running correctly on Vercel.</p>
                <hr>
                <p><a href="/admin/">Admin Panel</a> | <a href="/camp/">Game (Camp)</a></p>
            </div>
        </body>
    </html>
    '''
    return HttpResponse(html)
