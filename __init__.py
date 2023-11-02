from flask import Flask
from flask_mail import Mail
from flask_caching import Cache

app = Flask(__name__)
mail = Mail()
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Configure the Flask application
# You can add your configuration options here

mail.init_app(app)
cache.init_app(app)
