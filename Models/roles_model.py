from flask_sqlalchemy import SQLAlchemy
from . import db 

class Role(db.Model):
    __tablename__ = 'Role'

    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(100), nullable=False)
    SeniorityLevel = db.Column(db.Integer, nullable=False)
    Deleted = db.Column(db.Boolean, default=False)
