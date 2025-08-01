from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.extensions import db
from app.models.prompt import Prompt
from app.models.user import User
from app.models.like import Like
from app.models.follow import Follow
from sqlalchemy import func
from app.extensions import cache

prompt_bp=Blueprint('prompt',__name__)

@prompt_bp.route('',methods=['POST'])
@jwt_required()
def create_prompt():
    data=request.get_json()
    title=data.get('title')
    content=data.get('content')
    tags=data.get('tags',[])
    visibility=data.get('visibility','public')

    user_id=get_jwt_identity()

    new_prompt=Prompt(
        user_id=user_id,
        title=title,
        content=content,
        tags=tags,
        visibility=visibility
    )

    db.session.add(new_prompt)
    db.session.commit()

    return jsonify({"prompt":"new_prompt.serialize()"}),201

@prompt_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@cache.cached(timeout=60, query_string=True)  # Cache unique query combos for 60 sec
def list_prompts():
    user_id = get_jwt_identity()
    query = Prompt.query

    # Follower access logic
    if user_id:
        followed = db.session.query(Follow.followed_id).filter_by(follower_id=user_id).subquery()
        query = query.filter(
            (Prompt.visibility == 'public') |
            (Prompt.user_id == user_id) |
            ((Prompt.visibility == 'followers') & (Prompt.user_id.in_(followed)))
        )
    else:
        query = query.filter(Prompt.visibility == 'public')

    # Search + tag filters
    search = request.args.get('search')
    if search:
        query = query.filter(Prompt.search_vector.op('@@')(func.to_tsquery('english', search)))

    tag = request.args.get('tag')
    if tag:
        query = query.filter(Prompt.tags.any(tag))

    sort = request.args.get('sort')
    if sort == 'likes':
        from app.models.like import Like
        query = query.outerjoin(Like, Prompt.id == Like.prompt_id).group_by(Prompt.id)
        query = query.order_by(func.count(Like.user_id).desc())
    else:
        query = query.order_by(Prompt.created_at.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "page": page,
        "total": paginated.total,
        "prompts": [p.serialize() for p in paginated.items]
    })



from app.utils.markdown import render_markdown

@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
@jwt_required(optional=True)
def get_prompt(prompt_id):
    user_id = get_jwt_identity()
    prompt = Prompt.query.get_or_404(prompt_id)

    if prompt.visibility == 'private' and prompt.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    elif prompt.visibility == 'followers' and prompt.user_id != user_id:
        from app.models.follow import Follow
        is_follower = Follow.query.filter_by(follower_id=user_id, followed_id=prompt.user_id).first()
        if not is_follower:
            return jsonify({"msg": "Unauthorized"}), 403

    data = prompt.serialize()
    data["html"] = render_markdown(data["content"])
    return jsonify(data)


@prompt_bp.route('/<int:prompt_id>/fork',methods=['POST'])
@jwt_required()
def fork_prompt(prompt_id):
    parent_prompt=Prompt.query.get_or_404(prompt_id)
    user_id=get_jwt_identity()

    data=request.get_json() or {}
    new_title=data.get('title',parent_prompt.title + '(fork)')
    new_content=data.get('content',parent_prompt.content)
    new_tags=data.get('tags',parent_prompt.tags)
    visibility=data.get('visibility',parent_prompt.visibility)

    latest_version=(
        db.session.query(db.func.max(Prompt.version))
        .filter_by(forked_from=parent_prompt.id)
        .scalar()
    ) or 1

    forked_prompt= Prompt(
        user_id=user_id,
        title=new_title,
        content=new_content,
        tags=new_tags,
        visibility=visibility,
        forked_from=parent_prompt.id,
        version=latest_version+1
    )
    
    db.session.add(forked_prompt)
    db.session.commit()

    return jsonify({
        "msg":"Prompt forked successfully",
        "fork": forked_prompt.serialize()
    }),201

@prompt_bp.route('/<int:prompt_id>/versions', methods=['GET'])
def prompt_versions(prompt_id):
    parent = Prompt.query.get_or_404(prompt_id)

    versions = Prompt.query.filter_by(forked_from=parent.id).order_by(Prompt.version).all()
    history = [parent.serialize()] + [v.serialize() for v in versions]

    return jsonify({
        "base_prompt": parent.title,
        "versions": history
    })

@prompt_bp.route('/<int:prompt_id>/like',methods=['POST'])
@jwt_required()
def like_prompt(prompt_id):
    user_id=get_jwt_identity()
    prompt=Prompt.query.get_or_404(prompt_id)

    like=Like.query.filter_by(user_id=user_id,prompt_id=prompt_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({"msg":"Unliked prompt"})
    else:
        new_like=Like(user_id=user_id,prompt_id=prompt_id)
        db.session.add(new_like)
        return jsonify({"msg":"Liked prompt"})
    