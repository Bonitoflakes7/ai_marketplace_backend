from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.follow import Follow
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:user_id>/follow',methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user=get_jwt_identity()

    if current_user==user_id:
        return jsonify({"msg":"You cannot follow yourself"}),400

    existing=Follow.query.filter_by(follower_id=current_user,followed_id=user_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"msg":"Unfollowed user"})
    else:
        follow=Follow(follower_id=current_user,followed_id=user_id)
        db.session.add(follow)
        db.session.commit()

        return jsonify({"msg":"Followed user"})
    