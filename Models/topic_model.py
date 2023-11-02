from flask_sqlalchemy import SQLAlchemy
from . import db 

class Topic(db.Model):
    __tablename__ = 'Topic'
    
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    Description = db.Column(db.String(100), nullable=False)
    Approved = db.Column(db.Boolean)
    NoOfViews = db.Column(db.Integer)
    Pending = db.Column(db.Boolean)
    PublishDate = db.Column(db.DateTime, nullable=False)
    SubjectId = db.Column(db.Integer, db.ForeignKey('Subject.id'), nullable=False)
    Deleted = db.Column(db.Boolean)
    
    def __repr__(self):
        return f"<Topic(id={self.id}, Name='{self.Name}')>"
