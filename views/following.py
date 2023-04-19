from flask import Response, request
from flask_restful import Resource
from models import Following, User,Post, db
import json

def get_path():
    return request.host_url + 'api/posts/'

def get_user_ids(user_id):
    following = Following.query.filter_by(user_id=user_id).all()
    user_ids = [rec.following_id for rec in following]
    user_ids.append(user_id)
    return user_ids

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        following = Following.query.filter(Following.user_id==self.current_user.id).all()
        following_list = [those_following.to_dict_following() for those_following in following]
        return Response(json.dumps(following_list), mimetype="application/json", status=200)

    def post(self): 
        body = request.get_json()
        # print(body)
        post_id = body.get('user_id')

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

        # print (bookmarks[0])
        # Check for duplicate following entries
        existing_following = Following.query.filter_by(user_id=self.current_user.id, following_id=post_id).first()
        if existing_following:
            return Response(json.dumps({'error': 'Following already exists.'}), status=400)
        
        # create a new bookmark
        new_following = Following(
            following_id = post_id,
            user_id = self.current_user.id, 
        )
        db.session.add(new_following)
        db.session.commit()

        return Response(json.dumps(new_following.to_dict_following()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # Check if id is a valid integer
        try:
            id = int(id)
        except ValueError:
            return Response(json.dumps({}), mimetype="application/json", status=404)

        # Fetch the bookmark
        bookmark = Following.query.get(id)

        # Check if the bookmark exists and belongs to the current user
        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({}), mimetype="application/json", status=404)

        # Delete the bookmark
        db.session.delete(bookmark)
        db.session.commit()

        return Response(json.dumps({}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
