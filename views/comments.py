from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        # print(body)
        if not body.get('post_id'):
            return Response(
                json.dumps({'error': 'No post_id provided.'}), status=400
            )
        # 1. Create:
        new_post = Comment(
            post_id = body.get('post_id'),
            text = body.get('text'),
            user_id=self.current_user.id
        )
        
        print(new_post)
        db.session.add(new_post)    # issues the insert statement
        db.session.commit()         # commits the change to the database and returns the id

        return Response(json.dumps(new_post.to_dict()), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        print(id)
        return Response(json.dumps({}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
