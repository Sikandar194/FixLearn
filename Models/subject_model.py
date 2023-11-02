from flask_sqlalchemy import SQLAlchemy
from . import db 

class Subject(db.Model):
    __tablename__ = 'Subject'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)
    NumberOfTopics = db.Column(db.Integer)
    ContributorId = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    Description = db.Column(db.String(100), nullable=False)
    PublishDate = db.Column(db.DateTime, nullable=False)
    Deleted = db.Column(db.Boolean)
    EditedOn = db.Column(db.DateTime)
    
    
    explanations = db.relationship('Explanation', backref='subject', lazy='dynamic')
    
    def __repr__(self):
        return f"<Subject(id={self.id}, Name='{self.Name}')>"
