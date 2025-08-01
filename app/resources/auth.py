from flask import Blueprint,request,jsonify
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token,create_refresh_token

auth_bp=Blueprint('auth',__name__)

@auth_bp.route('/register',methods=['POST'])
def register():
    data=request.get_json()
    username=data.get('username')
    email=data.get('email')
    password=data.get('password')

    if User.query.filter((User.username==username)|(User.email==email)).first():
        return jsonify({"msg":"User with email or username already exists"}),409
    
    new_user=User(username=username,email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg":"User Registered Successfully"}),201

@auth_bp.route('/login',methods=['POST'])
def login():
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')

    user=User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token=create_access_token(identity=user.id)
        refresh_token=create_refresh_token(identity=user.id)
        return jsonify({
            "access_token":access_token,
            "refresh_token":refresh_token,
            "user":user.serialize()
        })
    return jsonify({"msg":"Invalid username or password"}),401