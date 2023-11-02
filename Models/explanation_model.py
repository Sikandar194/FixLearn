from datetime import datetime
from . import db 

class Explanation(db.Model):
    __tablename__ = 'Explanation'
    
    id = db.Column(db.Integer, primary_key=True)

    Explanation = db.Column(db.Text, nullable=False)
    PublishDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ContributorId = db.Column(db.Integer, db.ForeignKey('User.id'))
    CategoryId = db.Column(db.Integer, db.ForeignKey('Category.Id'))
    Views = db.Column(db.Integer, default = 0)
    EditedOn = db.Column(db.DateTime,default = None)
    Approved = db.Column(db.Boolean, default = False)
    Pending = db.Column(db.Boolean, default = True)
    Deleted = db.Column(db.Boolean, default = False)
    Topic = db.Column(db.Text, nullable=False)
    ViewsLastMonth = db.Column(db.Integer, default = 0)
    ViewsToday = db.Column(db.Integer, default = 0)
    ViewsThisMonth = db.Column(db.Integer, default = 0)
    SubjectId = db.Column(db.Integer, db.ForeignKey('Subject.id'))
    
    def __repr__(self):
        return f"<Explanation(id={self.id}, PublishDate={self.PublishDate})>"
