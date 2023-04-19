from flask import Response, request
from flask_restful import Resource
from models import LikePost, Post, Following, db
from views import get_authorized_user_ids
import json

def get_user_ids(user_id):
    following = Following.query.filter_by(user_id=user_id).all()
    user_ids = [rec.following_id for rec in following]
    user_ids.append(user_id)
    return user_ids

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "bookmark" based on the data posted in the body 
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

        list_of_user_ids = get_user_ids(self.current_user.id)
        post = Post.query.get(post_id)

        if post is None or post.user_id not in list_of_user_ids:
            error_message = {
                'error': 'post {0} does not exist.'.format(post_id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)

        # check if post with post_id exists
        bookmarks = LikePost.query.filter_by(user_id=self.current_user.id).all()
        if post_id in [bookmark.post_id for bookmark in bookmarks]:
            return Response(json.dumps({'error': 'Like already exists.'}), status=400)

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
