from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from core.models import App, Review
from django.db.models import Count
from django.template import Template, Context

def status_view(request):
    """Simple status view showing database stats"""
    try:
        app_count = App.objects.count()
        review_count = Review.objects.count()

        if request.GET.get('format') == 'json':
            return JsonResponse({
                'status': 'success',
                'database': 'connected',
                'apps_count': app_count,
                'reviews_count': review_count,
                'message': 'Franklin Google Play Store Search App is running!'
            })

        # HTML Response
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Franklin Search App</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                .stat-box { background: #3498db; color: white; padding: 20px; border-radius: 5px; text-align: center; }
                .stat-number { font-size: 2em; font-weight: bold; display: block; }
                .links { margin-top: 30px; }
                .links a { color: #3498db; text-decoration: none; margin-right: 20px; font-weight: bold; }
                .links a:hover { text-decoration: underline; }
                .success { color: #27ae60; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Franklin Search App</h1>
                <p class="success">✅ Application is running successfully!</p>

                <div class="stats">
                    <div class="stat-box">
                        <span class="stat-number">{{ apps_count }}</span>
                        Google Play Apps
                    </div>
                    <div class="stat-box">
                        <span class="stat-number">{{ reviews_count }}</span>
                        User Reviews
                    </div>
                </div>

                <h2>📋 Features Available</h2>
                <ul>
                    <li>🔍 <strong>App Search:</strong> Search through {{ apps_count }} Google Play Store apps</li>
                    <li>💬 <strong>Review System:</strong> Browse and moderate {{ reviews_count }} user reviews</li>
                    <li>👥 <strong>Role-Based Access:</strong> Supervisor and Regular User roles</li>
                    <li>📊 <strong>Admin Interface:</strong> Full Django admin for data management</li>
                    <li>🤖 <strong>Text Similarity:</strong> Advanced search with PostgreSQL trigrams</li>
                </ul>

                <h2>🔗 Quick Links</h2>
                <div class="links">
                    <a href="/admin/">Admin Interface</a>
                    <a href="/?format=json">API Status (JSON)</a>
                </div>

                <h2>🐳 Docker Setup</h2>
                <p><strong>Database:</strong> PostgreSQL 15 running on port 5433</p>
                <p><strong>Web Server:</strong> Django 4.2.7 running on port 8000</p>

                <h2>📝 Next Steps</h2>
                <ol>
                    <li>Access the <a href="/admin/">Django Admin</a> using: <code>admin</code> / <code>[your_password]</code></li>
                    <li>Explore the App and Review models in the admin interface</li>
                    <li>Test the search functionality (to be implemented)</li>
                    <li>Create additional users with different roles</li>
                </ol>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        context = Context({'apps_count': app_count, 'reviews_count': review_count})
        return HttpResponse(template.render(context))

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Database connection error: {str(e)}'
        }, status=500)
