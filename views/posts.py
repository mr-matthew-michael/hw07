from flask import Response, request
from flask_restful import Resource
from models import Post, Following, db
from views import get_authorized_user_ids

import json

def get_path():
    return request.host_url + 'api/posts/'


def get_user_ids(user_id):
    following = Following.query.filter_by(user_id=user_id).all()
    user_ids = [rec.following_id for rec in following]
    user_ids.append(user_id)
    return user_ids

class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):
        user_ids = get_user_ids(self.current_user.id)
        try:
            limit = request.args.get('limit') or 20
            limit = int(limit)
        except:
            return Response(
                json.dumps({'error': 'No string for limit.'}), status=400
            )
        if limit > 50:
            return Response(
                json.dumps({'error': 'Bad data. Limit cannot exceed 20.'}), status=400
            )
        posts = Post.query.filter(Post.user_id.in_(user_ids)).limit(limit)
        return Response(json.dumps([post.to_dict() for post in posts]), mimetype="application/json", status=200)

    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        print(body)
        if not body.get('image_url'):
            return Response(
                json.dumps({'error': 'No image_url provided.'}), status=400
            )
        # 1. Create:
        new_post = Post(
            image_url = body.get('image_url'),
            user_id = self.current_user.id, # must be a valid user_id or will throw an error
            caption = body.get('caption'),
            alt_text = body.get('alt_text')
        )
        db.session.add(new_post)    # issues the insert statement
        db.session.commit()         # commits the change to the database and returns the id

        return Response(json.dumps(new_post.to_dict()), mimetype="application/json", status=201)
        
class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        

    def patch(self, id):
        # update post based on the data posted in the body 
        body = request.get_json()
        print(body)       
        post = Post.query.get(id)
        if post is None or post.user_id != self.current_user.id:
            error_message = {
                'error': 'post {0} does not exist.'.format(id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)
        else:
            if(body.get('image_url')):
                post.image_url = body.get('image_url')
            if(body.get('caption')):
                post.caption = body.get('caption')
            if(body.get('alt_text')):
                post.alt_text = body.get('alt_text')

            db.session.commit()         # commits the change to the database and returns the id

            print(post.to_dict())
            return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)


    def delete(self, id):
        # delete post where "id"=id
        return Response(json.dumps({}), mimetype="application/json", status=200)


    def get(self, id):
        # get the post based on the id
        # yourself and your friends
        post = Post.query.get(id)
        user_ids = get_user_ids(self.current_user.id)
        if  post is None or post.user_id not in user_ids:
            error_message = {
                'error': 'post {0} does not exist.'.format(id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)
        else:
            return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostListEndpoint, 
        '/api/posts', '/api/posts/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        PostDetailEndpoint, 
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )