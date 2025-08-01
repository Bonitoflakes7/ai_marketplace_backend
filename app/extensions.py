from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_caching import Cache

db=SQLAlchemy()
jwt=JWTManager()
bcrypt=Bcrypt()
migrate=Migrate()
cache=Cache()

