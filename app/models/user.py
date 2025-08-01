from app.extensions import db,bcrypt
from datetime import datetime

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password_hash=db.Column(db.String(100),nullable=False)
    bio=db.Column(db.Text)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)


    def set_password(self,password):
        self.password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)
    
    def serialize(self):
        return{
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "bio":self.bio,
            "created_at":self.created_at.isoformat(),

        }