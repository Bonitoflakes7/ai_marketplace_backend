from flask import Flask
from .config import Config
from .extensions import db,jwt,bcrypt,migrate,cache
from .resources.auth import auth_bp
from .resources.prompt import prompt_bp
from .resources.user import user_bp

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app,db)
    cache.init_app(app)


    app.register_blueprint(auth_bp,url_prefix='/auth')
    app.register_blueprint(prompt_bp,url_prefix='/prompts')
    app.register_blueprint(user_bp,url_prefix='/users')


    return app

