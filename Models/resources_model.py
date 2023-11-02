from flask_sqlalchemy import SQLAlchemy
from . import db 

class Resource(db.Model):
    __tablename__ = 'Resource'
    
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    ResourcePath = db.Column(db.String(200), nullable=False)
    TopicId = db.Column(db.Integer, db.ForeignKey('Topic.id'), nullable=False)
    SubjectId = db.Column(db.Integer, db.ForeignKey('Subject.id'), nullable=False)
    ExplanationId = db.Column(db.Integer, db.ForeignKey('Explanation.id'), nullable=False)
    Downloads = db.Column(db.Integer)
    Deleted = db.Column(db.Boolean)
    
    def __repr__(self):
        return f"<Resource(id={self.id}, Name='{self.Name}', ResourcePath='{self.ResourcePath}')>"
