# 3rd party
from flask_restful import Resource
# project
from union_prototype import db_interface


class Parallel(Resource):
    def __init__(self):
        pass

    def get(self, obj_id=None, test=None):
        if test is None:
            return {'hello': obj_id}
        else:
            return {'test': test}

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass


class Cloud(Resource):
    def __init__(self):
        pass

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass
