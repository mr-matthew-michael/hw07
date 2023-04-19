from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        following = Following.query.filter(Following.user_id==self.current_user.id).all()
        following_list = [those_following.to_dict_following() for those_following in following]
        return Response(json.dumps(following_list), mimetype="application/json", status=200)

    def post(self):
            # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()
        print(body)
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
        # check if post with post_id exists
        bookmarks = Following.query.filter_by(user_id=self.current_user.id).all()
        if post_id in [bookmark.post_id for bookmark in bookmarks]:
            return Response(json.dumps({'error': 'Bookmark already exists.'}), status=400)
        
        post = Following.query.get(post_id)
        
        if post is None :
            error_message = {
                'error': 'post {0} does not exist.'.format(id)
            }
            return Response(json.dumps(error_message), mimetype="application/json", status=404)
    
        # create a new bookmark
        new_bookmark = Following(user_id=post_id)
        db.session.add(new_bookmark)
        db.session.commit()
    
        # return the newly created bookmark
        return Response(json.dumps(new_bookmark.to_dict()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        print(id)
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
