from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import get_authorized_user_ids

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        post_id = body.get('post_id')
        if post_id is None:
            return Response(
                json.dumps({'error': 'No post_id provided.'}), status=400
            )
        try:
            post_id = int(post_id)
        except ValueError:
            return Response(
                json.dumps({'error': 'Invalid post_id format.'}), status=400
            )

        # check if post_id exists
        post = Post.query.get(post_id)
        if post is None or post.user_id != self.current_user.id:
            error_message = {
                'error': 'post {0} does not exist.'.format(id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)

        text = body.get('text')
        if text is None:
            return Response(
                json.dumps({'error': 'No text provided.'}), status=400
            )

        # 1. Create:
        new_post = Comment(
            post_id=post_id,
            text=body.get('text'),
            user_id=self.current_user.id
        )
        
        db.session.add(new_post)    # issues the insert statement
        db.session.commit()         # commits the change to the database and returns the id

        return Response(json.dumps(new_post.to_dict()), mimetype="application/json", status=201)

        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        post = Comment.query.get(id)
        if post is None:
            return Response(json.dumps({'error': 'Comment not found.'}), mimetype="application/json", status=404)

        if post.user_id != self.current_user.id:
            return Response(json.dumps({'error': 'Unauthorized to delete comment.'}), mimetype="application/json", status=404)

        db.session.delete(post)
        db.session.commit()

        return Response(json.dumps({'message': 'Comment deleted.'}), mimetype="application/json", status=200)


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
