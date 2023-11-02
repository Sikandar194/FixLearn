from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import your models so that they are registered with the db instance
from .user_model import User
from .roles_model import Role
from .topic_model import Topic
from .resources_model import Resource
from .explanation_model import Explanation