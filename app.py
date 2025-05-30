import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure app settings
app.config['JSON_SORT_KEYS'] = False

# Import and register blueprints
from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Import routes
import routes
