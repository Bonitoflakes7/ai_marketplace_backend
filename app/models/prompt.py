from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Index
from sqlalchemy import event
from sqlalchemy.sql import func

class Prompt(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    title=db.Column(db.String(225),nullable=False)
    content=db.Column(db.Text,nullable=False)
    tags=db.Column(db.ARRAY(db.String),default=[])

    visibility=db.Column(db.String(20),default='public')

    version=db.Column(db.Integer,default=1)
    forked_from=db.Column(db.Integer,db.ForeignKey('prompt.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='prompts', lazy=True)
    parent_prompt = db.relationship('Prompt', remote_side=[id])

    search_vector=db.Column(TSVECTOR)


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "visibility": self.visibility,
            "version": self.version,
            "forked_from": self.forked_from,
            "created_at": self.created_at.isoformat()
        }

__table_args__ = (
    Index('ix_prompt_search_vector', 'search_vector', postgresql_using='gin'),
)

@event.listens_for(Prompt, 'before_insert')
@event.listens_for(Prompt, 'before_update')
def update_search_vector(mapper, connection, target):
    content = target.title + ' ' + target.content
    target.search_vector = func.to_tsvector('english', content)