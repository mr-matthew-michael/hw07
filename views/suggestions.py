from flask import Response, request
from flask_restful import Resource
from models import User
from views import get_authorized_user_ids
import json

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        authorized_user_ids = get_authorized_user_ids(self.current_user)
        suggestions = User.query.filter(User.id.notin_(authorized_user_ids)).limit(7).all()
        suggestions_data = [suggestion.to_dict() for suggestion in suggestions]
        return Response(json.dumps(suggestions_data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint, 
        '/api/suggestions', 
        '/api/suggestions/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
