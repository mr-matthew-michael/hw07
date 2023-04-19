from flask import Response, request
from flask_restful import Resource
from models import LikePost, db
import json

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()
        print(body)
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
        # check if post with post_id exists
        bookmarks = LikePost.query.filter_by(user_id=self.current_user.id).all()
        if post_id in [bookmark.post_id for bookmark in bookmarks]:
            return Response(json.dumps({'error': 'Bookmark already exists.'}), status=400)
        
        post = LikePost.query.get(post_id)
        
        if post is None :
            error_message = {
                'error': 'post {0} does not exist.'.format(id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)
    
        # create a new bookmark
        new_bookmark = LikePost(post_id=post_id, user_id=self.current_user.id)
        db.session.add(new_bookmark)
        db.session.commit()
    
        # return the newly created bookmark
        return Response(json.dumps(new_bookmark.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # Check if id is a valid integer
        try:
            id = int(id)
        except ValueError:
            return Response(json.dumps({}), mimetype="application/json", status=404)

        # Fetch the bookmark
        bookmark = LikePost.query.get(id)

        # Check if the bookmark exists and belongs to the current user
        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({}), mimetype="application/json", status=404)

        # Delete the bookmark
        db.session.delete(bookmark)
        db.session.commit()

        return Response(json.dumps({}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
