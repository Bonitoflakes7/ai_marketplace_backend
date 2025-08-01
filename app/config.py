import os

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY','supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/promptdb')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY','anothersecret')
    CACHE_TYPE='redis'
    CACHE_REDIS_URL=os.getenv('REDIS_URL','redis://localhost:6397/0')

    
