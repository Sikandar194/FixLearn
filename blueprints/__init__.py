from flask import Flask
from flask_mail import Mail
from flask_caching import Cache

app = Flask(__name__)
mail = Mail()
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Configure the Flask application

# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = 'bizintro1@gmail.com',
#     MAIL_PASSWORD = "mcgjjvnhbfbrabgo"
# )

mail.init_app(app)
cache.init_app(app)