from app.extensions import db

class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
