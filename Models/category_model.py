from datetime import datetime
from . import db 
class Category(db.Model):
    __tablename__ = 'Category'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"