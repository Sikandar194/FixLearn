import redis
import logging
from Models import db
from flask import Flask
from celery import Celery
from config import Config
from flask_mail import Mail
from flask_caching import Cache
from flask_session import Session
from blueprints.user.user import user_bp
from blueprints.roles.role import role_bp
from blueprints.admin.admin import admin_bp
from blueprints.contributor.contributor import contributor_bp

app = Flask(__name__)


app.config.from_object(Config)

app.jinja_env.autoescape = True

# Initialize and configure CSRF protection
#csrf = CSRFProtect(app)
# app.config['SESSION_COOKIE_SECURE'] = True  # Requires HTTPS
# app.config['SESSION_COOKIE_HTTPONLY'] = True  # Restricts cookie access to JavaScript


# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='app.log', level=logging.DEBUG, format=log_format)

# Create a logger instance for your application
logger = logging.getLogger(__name__)

#app.config['SECRET_KEY'] = 'your-secret-key'



# app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BSQL+Server+Native+Client+11.0%7D%3BServer%3DDESKTOP-RGGQBCN%5CSQLEXPRESS%3BDatabase%3DCourse%3BTrusted_Connection%3Dyes%3BPort%3D1433"
# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = 'bizintro1@gmail.com',
#     MAIL_PASSWORD = "mcgjjvnhbfbrabgo"
# )


# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    result=app.config['CELERY_RESULT_BACKEND']
)

# Load Celery configuration from the celeryconfig.py file
celery.config_from_object('celeryconfig')





# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = True  # To use Redis as a session store, it's typically not permanent
# app.config['SESSION_USE_SIGNER'] = True  # Use session signing for security (optional)
# app.config['SESSION_KEY_PREFIX'] = 'your_prefix:'  # Set a custom session key prefix (optional)

# Configure the Redis server for Flask-Session

# app.config['SESSION_REDIS'] = redis.StrictRedis(
#     host='localhost',
#     port=6379,
#     db=0  # The Redis database number to use
# )

Session(app)

mail = Mail()
mail.init_app(app)





app.register_blueprint(user_bp) 
app.register_blueprint(role_bp, url_prefix="/role")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(contributor_bp, url_prefix="/contributor")

db.init_app(app)


if __name__ =="__main__":
    app.run(debug=True)
    
